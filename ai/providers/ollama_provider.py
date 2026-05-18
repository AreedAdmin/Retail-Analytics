# AI-assisted: reviewed by [name]
"""
OllamaProvider — local Llama 3.1 via Ollama HTTP API.

Sends a two-message chat request (system + user) to the
Ollama server running on localhost and returns an LlmResponse.
"""
import time
import requests

from ai.config.settings import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    MAX_OUTPUT_TOKENS,
    TEMPERATURE,
    TIMEOUT_SECONDS,
)
from .base import LlmProvider, LlmProviderError, LlmResponse


class OllamaProvider(LlmProvider):
    name = "ollama"

    def generate(self, system_prompt: str, user_prompt: str) -> LlmResponse:
        url = f"{OLLAMA_HOST}/api/chat"
        payload = {
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "options": {
                "temperature": TEMPERATURE,
                "num_predict": MAX_OUTPUT_TOKENS,
            },
        }
        t0 = time.monotonic()
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise LlmProviderError(f"Ollama request failed: {exc}") from exc

        latency_ms = int((time.monotonic() - t0) * 1000)
        data = resp.json()

        text = data.get("message", {}).get("content", "").strip()
        usage = data.get("usage", {})
        return LlmResponse(
            text=text,
            model=OLLAMA_MODEL,
            provider="ollama",
            latency_ms=latency_ms,
            tokens_in=usage.get("prompt_tokens"),
            tokens_out=usage.get("completion_tokens"),
            raw=data,
        )

    def health_check(self) -> bool:
        try:
            resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m.get("name", "") for m in resp.json().get("models", [])]
            return any(OLLAMA_MODEL in m for m in models)
        except Exception:
            return False
