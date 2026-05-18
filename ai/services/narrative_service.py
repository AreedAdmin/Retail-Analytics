"""
Narrative service — single entry point for all dashboard AI features.
=====================================================================
Wires together the four Phase-3 pieces:

    prompts (ai/prompts/*.txt)
      + context_builder  (grounding from real model outputs)
      + llm_client        (free open model / API / offline stub)
      + guardrail         (numeric check + label enforcement)

Public API used by dashboard/modules/chat_interface.py:

    chat(message, history, scope)   -> grounded Q&A (Module 8a)
    summarise_scope(scope)          -> click-to-summarise (Module 8b)
    multi_summary(scopes)           -> multi-select briefing (Module 8c)
    backend_label()                 -> string for the UI footer
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from ai.services.llm_client import get_llm_client
from ai.services import context_builder, guardrail

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt template missing: {path}")
    return path.read_text(encoding="utf-8")


def backend_label() -> str:
    return get_llm_client().describe()


# ── Module 8a: grounded chat ─────────────────────────────────────────────────

def chat(message: str, history: List[Any], scope: str = "all") -> str:
    """
    Answer a manager question, grounded in the selected module's context.
    `scope` is a key from context_builder.available_scopes() or "all".
    """
    if not message or not message.strip():
        return "Ask me about the dashboard's KPIs, promotions or forecasts."

    if scope == "all":
        ctx = context_builder.build_multi_context(context_builder.available_scopes())
    else:
        ctx = context_builder.build_context(scope)

    system = load_prompt("chat_system.txt")
    user = (
        "CONTEXT\n-------\n"
        f"{json.dumps(ctx, indent=2)}\n\n"
        f"USER QUESTION: {message.strip()}"
    )

    raw = get_llm_client().generate(system=system, user=user, max_tokens=500)
    safe, _ = guardrail.apply(raw, ctx, module=f"chat:{scope}", prompt=message)
    return safe


# ── Module 8b: click-to-summarise a single chart/module ──────────────────────

def summarise_scope(scope: str) -> str:
    return summarise_payload(context_builder.build_context(scope),
                             module=f"summarise:{scope}")


def summarise_payload(ctx: dict, module: str = "summarise:payload") -> str:
    """
    Click-to-summarise for an arbitrary, already-grounded context dict
    (used by modules that build their context on the fly, e.g. the
    Scenario Simulator). Same prompt + guardrail path as summarise_scope.
    """
    template = load_prompt("click_to_summarise.txt")
    user = template.replace("{context_json}", json.dumps(ctx, indent=2))

    raw = get_llm_client().generate(
        system="You are a precise retail analytics summariser.",
        user=user,
        max_tokens=300,
    )
    safe, _ = guardrail.apply(raw, ctx, module=module, prompt=template)
    return safe


# ── Module 8c: multi-select integrated briefing ──────────────────────────────

def multi_summary(scopes: List[str]) -> str:
    if not scopes:
        return "Select at least one module to summarise.\n\n[Data-grounded]"
    ctx = context_builder.build_multi_context(scopes)
    template = load_prompt("multi_select_summary.txt")
    user = template.replace("{context_json}", json.dumps(ctx, indent=2))

    raw = get_llm_client().generate(
        system="You are a precise retail analytics summariser.",
        user=user,
        max_tokens=500,
    )
    safe, _ = guardrail.apply(
        raw, ctx, module=f"multi:{'+'.join(scopes)}", prompt=template
    )
    return safe


# ── Backwards-compatible Module 7 narrative ──────────────────────────────────

def generate_lift_narrative(context_override: Dict[str, Any] | None = None) -> str:
    """
    Module 7 promotion-lift narrative. Kept here so module7_ai_narrative.py
    is a thin shim and the prompt/guardrail path is shared with chat.
    """
    ctx = context_override or context_builder.build_promotion_context()
    template = load_prompt("module7_lift_narrative.txt")
    prompt_body = template.replace("{context_json}", json.dumps(ctx, indent=2))

    # The module-7 template embeds its own SYSTEM section, so pass it as user.
    raw = get_llm_client().generate(
        system="You are an expert retail analytics assistant.",
        user=prompt_body,
        max_tokens=600,
    )
    safe, _ = guardrail.apply(raw, ctx, module="module_7", prompt=prompt_body)
    return safe
