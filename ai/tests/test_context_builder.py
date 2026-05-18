# AI-assisted: reviewed by [name]
"""Tests for ai/context/context_builder.py."""
import pytest

from ai.context.context_builder import build_chat_context, build_chart_context
from ai.context.context_registry import resolve_context_path


def test_registry_hit():
    """module7_lift_summary should resolve to a file that exists."""
    path = resolve_context_path("module7_lift_summary")
    assert path is not None
    assert path.exists()


def test_registry_miss_returns_none():
    """An unknown chart_id must return None, not raise."""
    path = resolve_context_path("nonexistent_chart_xyz")
    assert path is None


def test_build_chat_context_has_module7():
    ctx = build_chat_context()
    assert "module_7_promotion_lift" in ctx


def test_build_chat_context_missing_key():
    ctx = build_chat_context()
    # Future modules that don't have files yet should appear in _missing.
    if "_missing" in ctx:
        assert isinstance(ctx["_missing"], list)


def test_build_chart_context_from_registry():
    ctx = build_chart_context("module7_lift_summary")
    assert ctx is not None
    assert "module_name" in ctx
    assert "chart_id" in ctx
    assert "metrics" in ctx
    assert "key_findings" in ctx


def test_build_chart_context_missing_returns_none():
    ctx = build_chart_context("nonexistent_chart_xyz")
    assert ctx is None


def test_build_chart_context_live_data_override():
    """When chart_data is supplied, it is used directly without hitting disk."""
    live = {"metrics": {"value": 42}, "key_findings": ["test finding"]}
    ctx = build_chart_context("module7_lift_summary", chart_data=live)
    assert ctx is not None
    assert ctx["metrics"]["value"] == 42
    assert ctx["key_findings"] == ["test finding"]
