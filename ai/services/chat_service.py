# AI-assisted: reviewed by [name]
"""
chat_service — orchestrates one chat turn end-to-end.

Pipeline:
  1. run_input_filter      → refuse or continue
  2. build_chat_context    → dict of all available module contexts
  3. load_prompt           → format system_chat.txt with context
  4. get_provider().generate → LlmResponse (falls back to Echo)
  5. validate_output       → clean text + flags
  6. log_interaction       → JSONL + CSV
  7. return ChatResult
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from ai.config.settings import PROMPTS_DIR
from ai.context.context_builder import build_chat_context
from ai.guardrails.input_filter import run_input_filter
from ai.guardrails.output_validator import validate_output
from ai.guardrails.refusal_messages import get_refusal
from ai.logs.interaction_logger import log_interaction
from ai.providers import get_provider
from ai.providers.base import LlmProviderError

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT_ID = "system_chat_v1"


@dataclass
class ChatResult:
    answer: str
    label: str
    flags: dict = field(default_factory=dict)
    provider: str = "echo"
    model: str = "echo-v1"
    latency_ms: int = 0
    refusal_reason: str | None = None
    event_id: str = ""


def _load_prompt(filename: str) -> str:
    path: Path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def _extract_label(text: str) -> str:
    if "[Data-grounded]" in text:
        return "Data-grounded"
    if "[General inference]" in text:
        return "General inference"
    return "General inference"


def answer_question(user_query: str, session_id: str) -> ChatResult:
    """Main entry point. Returns a ChatResult for a single turn."""

    # ── 1. Input filter ──────────────────────────────────────────
    filter_result = run_input_filter(user_query)
    if not filter_result.allowed:
        refusal_text = get_refusal(
            filter_result.reason,
            n=len(user_query),
            max=1200,
        )
        eid = log_interaction(
            session_id=session_id,
            event_type="refusal",
            user_query=user_query,
            context_modules=[],
            provider="n/a",
            model="n/a",
            system_prompt_id=_SYSTEM_PROMPT_ID,
            latency_ms=0,
            tokens_in=None,
            tokens_out=None,
            answer_label="n/a",
            answer_text=refusal_text,
            guardrail_input={"allowed": False, "reason": filter_result.reason},
            guardrail_output={
                "unverified_numbers": [],
                "label_auto_added": False,
                "system_leak_redacted": False,
            },
            refusal_reason=filter_result.reason,
        )
        return ChatResult(
            answer=refusal_text,
            label="n/a",
            refusal_reason=filter_result.reason,
            event_id=eid,
        )

    # ── 2. Build context ─────────────────────────────────────────
    context = build_chat_context()
    context_modules = [k for k in context if k != "_missing"]
    context_json = json.dumps(context, indent=2)

    # ── 3. Load and format prompt ────────────────────────────────
    template = _load_prompt("system_chat.txt")
    system_prompt = template.replace("{context_json}", context_json)

    # ── 4. Generate ──────────────────────────────────────────────
    provider_name = "echo"
    model_name = "echo-v1"
    latency_ms = 0
    tokens_in = None
    tokens_out = None
    error_str = None
    raw_text = ""

    try:
        provider = get_provider()
        resp = provider.generate(system_prompt, user_query)
        raw_text = resp.text
        provider_name = resp.provider
        model_name = resp.model
        latency_ms = resp.latency_ms
        tokens_in = resp.tokens_in
        tokens_out = resp.tokens_out
    except LlmProviderError as exc:
        error_str = str(exc)
        refusal_text = get_refusal("provider_down")
        eid = log_interaction(
            session_id=session_id,
            event_type="error",
            user_query=user_query,
            context_modules=context_modules,
            provider=provider_name,
            model=model_name,
            system_prompt_id=_SYSTEM_PROMPT_ID,
            latency_ms=0,
            tokens_in=None,
            tokens_out=None,
            answer_label="n/a",
            answer_text=refusal_text,
            guardrail_input={"allowed": True, "reason": None},
            guardrail_output={
                "unverified_numbers": [],
                "label_auto_added": False,
                "system_leak_redacted": False,
            },
            refusal_reason="provider_down",
            error=error_str,
        )
        return ChatResult(
            answer=refusal_text,
            label="n/a",
            refusal_reason="provider_down",
            event_id=eid,
        )

    # ── 5. Validate output ───────────────────────────────────────
    clean_text, flags = validate_output(raw_text, context)
    label = _extract_label(clean_text)

    # ── 6. Log ───────────────────────────────────────────────────
    eid = log_interaction(
        session_id=session_id,
        event_type="chat_query",
        user_query=user_query,
        context_modules=context_modules,
        provider=provider_name,
        model=model_name,
        system_prompt_id=_SYSTEM_PROMPT_ID,
        latency_ms=latency_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        answer_label=label,
        answer_text=clean_text,
        guardrail_input={"allowed": True, "reason": None},
        guardrail_output=flags,
        error=error_str,
    )

    # ── 7. Return ────────────────────────────────────────────────
    return ChatResult(
        answer=clean_text,
        label=label,
        flags=flags,
        provider=provider_name,
        model=model_name,
        latency_ms=latency_ms,
        event_id=eid,
    )
