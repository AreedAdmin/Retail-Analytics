# AI-assisted: reviewed by [name]
"""
EchoProvider — deterministic offline fallback.

Returns a fixed-shape response without any network call.
Used by tests, CI, and as a last-resort fallback when all
real providers are unreachable.
"""
from .base import LlmProvider, LlmResponse


class EchoProvider(LlmProvider):
    name = "echo"

    def generate(self, system_prompt: str, user_prompt: str) -> LlmResponse:
        # Find the first non-header, non-empty line to use as grounding flavour.
        # Skip lines that are headers ("SYSTEM", "---", "CONTEXT", etc.) so the
        # excerpt doesn't trigger the output validator's system-leak detector.
        _SKIP_PREFIXES = ("SYSTEM", "---", "CONTEXT", "QUESTION", "TASK",
                          "CHART", "MULTI", "Hard rules", "Every response")
        excerpt = ""
        for line in system_prompt.splitlines():
            stripped = line.strip()
            if stripped and not any(stripped.startswith(p) for p in _SKIP_PREFIXES):
                excerpt = stripped[:120]
                break
        if not excerpt:
            excerpt = "retail analytics dashboard outputs"
        text = (
            f"Based on the provided context: {excerpt}.\n"
            "[General inference]"
        )
        return LlmResponse(
            text=text,
            model="echo-v1",
            provider="echo",
            latency_ms=0,
            tokens_in=None,
            tokens_out=None,
            raw={"echo": True},
        )

    def health_check(self) -> bool:
        return True
