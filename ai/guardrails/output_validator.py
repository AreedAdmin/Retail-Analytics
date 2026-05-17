# AI-assisted: reviewed by [name]
"""
Output validator — post-generation checks on LLM responses.

Never raises — always returns (clean_text, flags_dict).
"""
import json
import re


_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)*\b")

_SYSTEM_LEAK_MARKERS: list[str] = [
    "SYSTEM",
    "system prompt",
    "You are an expert retail analytics",
]


def extract_numbers(text: str) -> list[str]:
    """Return all number tokens from text, with commas stripped."""
    return [m.replace(",", "") for m in _NUMBER_RE.findall(text)]


def _numbers_from_context(context_str: str) -> list[float]:
    """Extract all numeric values found anywhere in the context string."""
    raw = _NUMBER_RE.findall(context_str)
    floats: list[float] = []
    for r in raw:
        try:
            floats.append(float(r.replace(",", "")))
        except ValueError:
            pass
    return floats


def numbers_in_context(numbers: list[str], context_str: str) -> list[str]:
    """
    Return numbers from the response that cannot be verified in context.

    A number is verified if it either appears as an exact string in context
    OR its float value is within 0.5% of any float found in context.
    """
    context_floats = _numbers_from_context(context_str)
    unverified: list[str] = []

    for num_str in numbers:
        # Exact string match first.
        if num_str in context_str:
            continue
        # Numeric tolerance check (0.5%).
        try:
            val = float(num_str)
        except ValueError:
            unverified.append(num_str)
            continue
        if val == 0:
            # 0 is common and not meaningful to verify.
            continue
        verified = any(
            abs(val - cf) / max(abs(cf), 1e-9) <= 0.005
            for cf in context_floats
        )
        if not verified:
            unverified.append(num_str)

    return unverified


def enforce_label(text: str, unverified_numbers: list[str]) -> tuple[str, bool]:
    """
    Ensure the response ends with a label line.

    If unverified numbers exist, force [General inference] regardless of
    what the model wrote.  Returns (labelled_text, label_auto_added).
    """
    label_auto_added = False

    has_data_grounded   = "[Data-grounded]" in text
    has_general         = "[General inference]" in text

    if unverified_numbers:
        # Strip any existing [Data-grounded] and ensure [General inference].
        text = text.replace("[Data-grounded]", "").rstrip()
        if not has_general:
            text = text + "\n[General inference]"
            label_auto_added = True
        return text, label_auto_added

    if not has_data_grounded and not has_general:
        text = text + "\n[General inference]"
        label_auto_added = True

    return text, label_auto_added


def redact_system_leak(text: str) -> tuple[str, bool]:
    """
    Remove any line that looks like the model echoed the system prompt.

    Returns (clean_text, system_leak_redacted).
    """
    lines = text.splitlines()
    clean_lines = []
    redacted = False
    for line in lines:
        if any(marker in line for marker in _SYSTEM_LEAK_MARKERS):
            redacted = True
        else:
            clean_lines.append(line)
    return "\n".join(clean_lines), redacted


def validate_output(text: str, context: dict | None = None) -> tuple[str, dict]:
    """
    Run all output checks and return (clean_text, flags_dict).

    flags_dict keys: unverified_numbers, label_auto_added, system_leak_redacted.
    """
    context_str = json.dumps(context) if context else ""

    # 1. Redact system leaks.
    text, system_leak_redacted = redact_system_leak(text)

    # 2. Extract and verify numbers.
    numbers = extract_numbers(text)
    unverified = numbers_in_context(numbers, context_str)

    # 3. Enforce label.
    text, label_auto_added = enforce_label(text, unverified)

    flags = {
        "unverified_numbers":   unverified,
        "label_auto_added":     label_auto_added,
        "system_leak_redacted": system_leak_redacted,
    }
    return text, flags
