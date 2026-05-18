"""
Module 7 — AI Narrative Service (compatibility shim)
====================================================
The real logic now lives in ai/services/narrative_service.py, which shares
one prompt + guardrail + LLM-backend path with the Module 8 chat interface.

This file is kept so existing callers/imports keep working:

    from ai.services.module7_ai_narrative import generate_lift_narrative
    from ai.services.module7_ai_narrative import summarise_chart

Backend is provider-agnostic and free by default (see llm_client.py):
no API key is required to run the dashboard.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from ai.services import narrative_service
from ai.services.llm_client import get_llm_client
from ai.services import guardrail


def generate_lift_narrative(context_override: Dict[str, Any] | None = None) -> str:
    """Module 7 promotion-lift narrative (delegates to narrative_service)."""
    return narrative_service.generate_lift_narrative(context_override)


def summarise_chart(chart_id: str, chart_data: Dict[str, Any]) -> str:
    """
    Click-to-summarise for an arbitrary Module 7 chart. The prompt is loaded
    from ai/prompts/click_to_summarise.txt (no inline prompt strings).
    """
    ctx = {
        "module_name": "module_7_promotion_lift",
        "chart_id": chart_id,
        "metrics": chart_data if isinstance(chart_data, dict) else {"data": chart_data},
        "key_findings": [],
    }
    template = narrative_service.load_prompt("click_to_summarise.txt")
    user = template.replace("{context_json}", json.dumps(ctx, indent=2))
    raw = get_llm_client().generate(
        system="You are a precise retail analytics summariser.",
        user=user,
        max_tokens=250,
    )
    safe, _ = guardrail.apply(raw, ctx, module="module_7_chart", prompt=template)
    return safe


if __name__ == "__main__":
    print("Backend:", get_llm_client().describe())
    print(generate_lift_narrative())
