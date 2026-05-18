# AI-assisted: reviewed by [name]
"""Tests for ai/guardrails/output_validator.py — 5+ cases."""
import pytest

from ai.guardrails.output_validator import (
    enforce_label,
    extract_numbers,
    numbers_in_context,
    redact_system_leak,
    validate_output,
)


def test_clean_response_no_changes():
    text = "The lift for SKU 38 is 59.42%.\n[Data-grounded]"
    context = {"key_findings": {"top_5_lift_skus": [{"sku_id": 38, "mean_lift_pct": 59.42}]}}
    clean, flags = validate_output(text, context)
    assert "[Data-grounded]" in clean
    assert flags["label_auto_added"] is False
    assert flags["system_leak_redacted"] is False


def test_missing_label_auto_added():
    text = "The median lift across SKUs is around 21%."
    clean, flags = validate_output(text, {})
    assert "[General inference]" in clean
    assert flags["label_auto_added"] is True


def test_hallucinated_number_forces_general_inference():
    text = "Revenue impact is 99999 units.\n[Data-grounded]"
    context = {"metrics": {"oos_mae": 65.333}}
    clean, flags = validate_output(text, context)
    assert "[General inference]" in clean
    assert "99999" in flags["unverified_numbers"]


def test_system_prompt_leak_redacted():
    text = "You are an expert retail analytics assistant.\nHere is the answer.\n[General inference]"
    clean, flags = validate_output(text, {})
    assert "You are an expert retail analytics" not in clean
    assert flags["system_leak_redacted"] is True
    assert "[General inference]" in clean


def test_label_override_on_unverified_numbers():
    text = "The forecast shows 12345 units demand.\n[Data-grounded]"
    context = {"metrics": {"y_pred": 100.0}}
    clean, flags = validate_output(text, context)
    # 12345 is not in context → label must be forced to General inference
    assert "[General inference]" in clean
    assert "[Data-grounded]" not in clean
    assert "12345" in flags["unverified_numbers"]


def test_extract_numbers():
    nums = extract_numbers("Revenue: 1,200 units, lift 59.42%, R² 0.215")
    assert "1200" in nums
    assert "59.42" in nums
    assert "0.215" in nums


def test_numbers_in_context_tolerance():
    # 59.42 is within 0.5% of 59.42 — should be verified.
    unverified = numbers_in_context(["59.42"], '{"mean_lift_pct": 59.42}')
    assert "59.42" not in unverified
