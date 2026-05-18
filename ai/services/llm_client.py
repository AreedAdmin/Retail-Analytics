"""
LLMClient — provider-agnostic chat/completion backend.
=====================================================
One client, many backends. The backend is resolved at runtime so the same
code runs free on Hugging Face Spaces and fast on a developer laptop:

    LLM_BACKEND = auto (default) | ollama | local | anthropic | openai | stub

Resolution order when LLM_BACKEND=auto:
    1. OLLAMA_API_KEY present           -> "ollama"     (Ollama Cloud, primary)
    2. ANTHROPIC_API_KEY present        -> "anthropic"  (fast local dev)
    3. OPENAI_API_KEY present           -> "openai"
    4. transformers importable          -> "local"      (free, in-Space)
    5. otherwise                        -> "stub"        (no deps, offline)

Ollama Cloud is the primary AI-narrative backend (see deploy.md, Layer 3).
Set OLLAMA_API_KEY (+ optional OLLAMA_MODEL, default "gpt-oss:120b-cloud",
OLLAMA_HOST default "https://ollama.com"). On failure, generate() degrades
through any configured API provider, then the offline stub.

Free deployment target (no API keys, no usage caps):
    - Free CPU Space:  LLM_MODEL_ID=Qwen/Qwen2.5-7B-Instruct
    - Free ZeroGPU:    LLM_MODEL_ID=Qwen/Qwen2.5-32B-Instruct  (set HAS_ZEROGPU)

The "stub" backend produces a deterministic, extractive answer straight from
the grounding context. It needs no model and no network, so the dashboard and
its tests always run — and it can never hallucinate.
"""

from __future__ import annotations

import os
import re
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MODEL = os.environ.get("LLM_MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")


# ── Backend resolution ───────────────────────────────────────────────────────

def resolve_backend() -> str:
    """Decide which backend to use from env + available dependencies."""
    forced = os.environ.get("LLM_BACKEND", "auto").strip().lower()
    if forced and forced != "auto":
        return forced

    if os.environ.get("OLLAMA_API_KEY"):
        return "ollama"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    try:
        import transformers  # noqa: F401
        return "local"
    except Exception:
        return "stub"


# ── Client ───────────────────────────────────────────────────────────────────

class LLMClient:
    """
    Unified text-generation client.

        client = LLMClient()
        text = client.generate(system="...", user="...", max_tokens=600)

    `generate()` never raises for backend/runtime problems — it returns a
    clearly-labelled fallback string so the dashboard never crashes.
    """

    def __init__(self, backend: Optional[str] = None, model_id: Optional[str] = None):
        self.backend = (backend or resolve_backend()).lower()
        self.model_id = model_id or DEFAULT_LOCAL_MODEL
        self._pipe = None  # lazily-built transformers pipeline
        logger.info("LLMClient backend=%s model=%s", self.backend, self.model_id)

    # -- public ---------------------------------------------------------------

    def describe(self) -> str:
        """Human-readable backend label for the UI footer."""
        if self.backend == "ollama":
            model = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b-cloud")
            return f"Ollama Cloud ({model})"
        if self.backend == "local":
            return f"local open model ({self.model_id})"
        if self.backend == "anthropic":
            return "Anthropic Claude API"
        if self.backend == "openai":
            return "OpenAI API"
        return "offline grounded extractor (stub)"

    def _dispatch(self, backend: str, system: str, user: str,
                  max_tokens: int) -> str:
        if backend == "ollama":
            return self._gen_ollama(system, user, max_tokens)
        if backend == "anthropic":
            return self._gen_anthropic(system, user, max_tokens)
        if backend == "openai":
            return self._gen_openai(system, user, max_tokens)
        if backend == "local":
            return self._gen_local(system, user, max_tokens)
        return self._gen_stub(system, user)

    def _fallback_chain(self) -> list:
        """API providers to try (in order) if the primary backend fails,
        before the offline stub. Only those with credentials present."""
        chain = []
        if self.backend != "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
            chain.append("anthropic")
        if self.backend != "openai" and os.environ.get("OPENAI_API_KEY"):
            chain.append("openai")
        return chain

    def generate(self, system: str, user: str, max_tokens: int = 600) -> str:
        try:
            return self._dispatch(self.backend, system, user, max_tokens)
        except Exception as e:  # never crash the dashboard
            logger.exception("LLM generation failed on backend=%s", self.backend)
            for fb in self._fallback_chain():
                try:
                    logger.warning("falling back to backend=%s", fb)
                    return self._dispatch(fb, system, user, max_tokens)
                except Exception:
                    logger.exception("fallback backend=%s failed", fb)
            return (
                f"⚠️ AI backend ({self.backend}) unavailable: {e}\n\n"
                "Falling back to a grounded extract of the available data:\n\n"
                f"{self._gen_stub(system, user)}"
            )

    # -- backends -------------------------------------------------------------

    def _gen_anthropic(self, system: str, user: str, max_tokens: int) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text.strip()

    def _gen_openai(self, system: str, user: str, max_tokens: int) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content.strip()

    def _gen_ollama(self, system: str, user: str, max_tokens: int) -> str:
        """Ollama Cloud (https://ollama.com) chat completion.

        Uses the `ollama` client with a bearer token. Model defaults to
        `gpt-oss:120b-cloud`; override via OLLAMA_MODEL. Deterministic
        (temperature 0) so narratives are stable for the same context.
        """
        from ollama import Client

        api_key = os.environ["OLLAMA_API_KEY"]
        host = os.environ.get("OLLAMA_HOST", "https://ollama.com")
        model = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b-cloud")
        timeout = float(os.environ.get("OLLAMA_TIMEOUT", "60"))

        client = Client(
            host=host,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            options={"temperature": 0, "num_predict": max_tokens},
        )
        # ollama returns a ChatResponse (attr access) or a dict, by version
        msg = getattr(resp, "message", None)
        if msg is None:
            msg = resp["message"]
        content = getattr(msg, "content", None)
        if content is None:
            content = msg["content"]
        return content.strip()

    def _build_local_pipe(self):
        """Build the transformers pipeline once. ZeroGPU-aware."""
        if self._pipe is not None:
            return self._pipe

        import torch  # noqa: F401
        from transformers import pipeline

        device_map = "auto"
        self._pipe = pipeline(
            "text-generation",
            model=self.model_id,
            torch_dtype="auto",
            device_map=device_map,
            trust_remote_code=True,
        )
        return self._pipe

    def _gen_local(self, system: str, user: str, max_tokens: int) -> str:
        pipe = self._build_local_pipe()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        def _run():
            out = pipe(
                messages,
                max_new_tokens=max_tokens,
                do_sample=False,
                temperature=None,
                top_p=None,
            )
            generated = out[0]["generated_text"]
            # transformers returns the full chat; take the last assistant turn
            if isinstance(generated, list):
                return generated[-1]["content"].strip()
            return str(generated).strip()

        # On a ZeroGPU Space, the heavy call must run inside an @spaces.GPU
        # context. We wrap lazily so importing this module never requires it.
        try:
            import spaces  # type: ignore

            return spaces.GPU(_run)()  # type: ignore[attr-defined]
        except Exception:
            return _run()

    def _gen_stub(self, system: str, user: str) -> str:
        """
        No-model fallback: deterministically surface the figures already
        present in the prompt's CONTEXT block. Cannot hallucinate because it
        only echoes supplied numbers.
        """
        ctx = user
        m = re.search(r"CONTEXT\s*[-\n]*\s*(\{.*\})", user, re.DOTALL)
        findings = []
        if m:
            try:
                data = json.loads(m.group(1))
                ctx = json.dumps(data, indent=2)
                metrics = data.get("metrics", {})
                for k, v in list(metrics.items())[:8]:
                    findings.append(f"- **{k}**: {v}")
                for f in (data.get("key_findings") or [])[:6]:
                    findings.append(f"- {f}" if isinstance(f, str) else f"- {json.dumps(f)}")
            except Exception:
                pass

        body = "\n".join(findings) if findings else ctx[:800]
        return (
            "Grounded summary (offline extractor — no LLM configured):\n\n"
            f"{body}\n\n"
            "Note: figures above are taken directly from the supplied model "
            "outputs. Configure LLM_MODEL_ID (free open model) or an API key "
            "for narrative phrasing.\n\n"
            "[Data-grounded]"
        )


# ── Singleton ────────────────────────────────────────────────────────────────

_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the process-wide LLMClient."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
