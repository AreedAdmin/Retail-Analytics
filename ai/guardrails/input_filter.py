# AI-assisted: reviewed by [name]
"""
Input guardrails — five sequential checks that run before every LLM call.

Each check returns an InputCheckResult. The caller runs them in order
and short-circuits on the first failure.
"""
import re
from dataclasses import dataclass

from ai.config.settings import MIN_QUERY_CHARS, MAX_INPUT_CHARS, TOPIC_ALLOWLIST


@dataclass
class InputCheckResult:
    allowed: bool
    reason: str | None
    which_check: str | None


# ── Load allowlist once at import time ───────────────────────────────────────

def _load_allowlist() -> list[str]:
    try:
        text = TOPIC_ALLOWLIST.read_text(encoding="utf-8")
        return [line.strip().lower() for line in text.splitlines() if line.strip()]
    except OSError:
        return []


_ALLOWLIST: list[str] = _load_allowlist()

# ── Prompt injection substrings ──────────────────────────────────────────────

_INJECTION_PHRASES: list[str] = [
    "ignore previous",
    "ignore the above",
    "disregard your instructions",
    "you are now",
    "system prompt",
    "reveal your prompt",
    "jailbreak",
    "dan mode",
    "developer mode",
]

# ── PII regexes ──────────────────────────────────────────────────────────────

_PII_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),   # email
    re.compile(r"\b(?:0|\+44)\s?(?:\d\s?){9,10}\b"),                          # UK phone
    re.compile(r"\b\d{11,}\b"),                                                # 11+ digit run
    re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b"),                           # IBAN-shaped
    re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b"),                              # basic card pattern
]

# ── Raw-data keywords ────────────────────────────────────────────────────────

_RAW_DATA_PHRASES: list[str] = [
    "list all rows",
    "dump",
    "export everything",
]


# ── Individual checks ────────────────────────────────────────────────────────

def check_length(text: str) -> InputCheckResult:
    if len(text) < MIN_QUERY_CHARS:
        return InputCheckResult(allowed=False, reason="length_too_short", which_check="length")
    if len(text) > MAX_INPUT_CHARS:
        return InputCheckResult(allowed=False, reason="length_too_long", which_check="length")
    return InputCheckResult(allowed=True, reason=None, which_check="length")


def check_pii(text: str) -> InputCheckResult:
    for pattern in _PII_PATTERNS:
        if pattern.search(text):
            return InputCheckResult(allowed=False, reason="pii", which_check="pii")
    return InputCheckResult(allowed=True, reason=None, which_check="pii")


def check_prompt_injection(text: str) -> InputCheckResult:
    lower = text.lower()
    for phrase in _INJECTION_PHRASES:
        if phrase in lower:
            return InputCheckResult(
                allowed=False, reason="prompt_injection", which_check="prompt_injection"
            )
    return InputCheckResult(allowed=True, reason=None, which_check="prompt_injection")


def check_topic(text: str) -> InputCheckResult:
    # Short queries always pass — "thanks" / "more detail" should not be blocked.
    if len(text) <= 80:
        return InputCheckResult(allowed=True, reason=None, which_check="topic")
    lower = text.lower()
    for term in _ALLOWLIST:
        if term in lower:
            return InputCheckResult(allowed=True, reason=None, which_check="topic")
    return InputCheckResult(allowed=False, reason="off_topic", which_check="topic")


def check_raw_data_dump(text: str) -> InputCheckResult:
    lower = text.lower()
    # Reject if query contains all of {raw, data, csv} together.
    if "raw" in lower and "data" in lower and "csv" in lower:
        return InputCheckResult(
            allowed=False, reason="raw_data_dump", which_check="raw_data_dump"
        )
    for phrase in _RAW_DATA_PHRASES:
        if phrase in lower:
            return InputCheckResult(
                allowed=False, reason="raw_data_dump", which_check="raw_data_dump"
            )
    return InputCheckResult(allowed=True, reason=None, which_check="raw_data_dump")


# ── Composite filter ─────────────────────────────────────────────────────────

def run_input_filter(text: str) -> InputCheckResult:
    """Run all checks in order; return first failure or a final allowed result."""
    for check_fn in (
        check_length,
        check_pii,
        check_prompt_injection,
        check_topic,
        check_raw_data_dump,
    ):
        result = check_fn(text)
        if not result.allowed:
            return result
    return InputCheckResult(allowed=True, reason=None, which_check=None)
