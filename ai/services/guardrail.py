"""
Guardrail — anti-hallucination post-processing for every AI response.
=====================================================================
Two checks run on every model output:

1. Numeric grounding: every number in the response is matched against the
   numbers present in the grounding context. Unmatched numbers are flagged.
2. Label enforcement: the response must end with [Data-grounded] or
   [General inference]. If missing, we append one — derived from check (1),
   not trusted blindly from the model.

Flagged outputs are appended to ai/services/failure_log.jsonl for Module 9
(Critical Reflection).
"""

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
FAILURE_LOG = REPO_ROOT / "ai" / "services" / "failure_log.jsonl"

_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
_LABEL_RE = re.compile(r"\[(Data-grounded|General inference)\]", re.IGNORECASE)


def _numbers(text: str) -> List[str]:
    # Normalise: strip thousands separators so "1,502" matches "1502"
    return _NUM_RE.findall(text.replace(",", ""))


def check_numeric_grounding(response: str, context: Dict[str, Any]) -> List[str]:
    """Return a list of warnings for numbers not traceable to the context."""
    ctx_numbers = set(_numbers(json.dumps(context)))
    # Round context numbers so 58.72 ~ 58.7 ~ 59 don't false-alarm
    ctx_rounded = set()
    for n in ctx_numbers:
        try:
            f = float(n)
            ctx_rounded.update({n, str(round(f)), str(round(f, 1))})
        except ValueError:
            ctx_rounded.add(n)

    warnings: List[str] = []
    for num in _numbers(response):
        if num in ctx_rounded:
            continue
        try:
            f = float(num)
            if str(round(f)) in ctx_rounded or str(round(f, 1)) in ctx_rounded:
                continue
            # ignore trivially-safe small integers (years, list counts, "2-3")
            if f.is_integer() and abs(f) <= 12:
                continue
        except ValueError:
            pass
        warnings.append(f"'{num}' not found in grounding context")
    return warnings


def enforce_label(response: str, has_warnings: bool) -> str:
    """
    Guarantee the response ends with a correct label line. The label is
    derived from the grounding check, not blindly trusted from the model.
    """
    correct = "[General inference]" if has_warnings else "[Data-grounded]"
    stripped = _LABEL_RE.sub("", response).rstrip()
    return f"{stripped}\n\n{correct}"


def log_failure(module: str, prompt: str, response: str, warnings: List[str]) -> None:
    FAILURE_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "module": module,
        "prompt_excerpt": prompt[:200],
        "response_excerpt": response[:300],
        "warnings": warnings,
    }
    with open(FAILURE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def apply(
    response: str,
    context: Dict[str, Any],
    module: str,
    prompt: str = "",
) -> Tuple[str, List[str]]:
    """
    Run all guardrails. Returns (safe_response, warnings).
    Logs to failure_log.jsonl when warnings are present.
    """
    warnings = check_numeric_grounding(response, context)
    safe = enforce_label(response, has_warnings=bool(warnings))
    if warnings:
        log_failure(module, prompt or "", response, warnings)
    return safe, warnings
