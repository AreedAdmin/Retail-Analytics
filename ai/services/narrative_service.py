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
from ai.services import context_builder, guardrail, telemetry

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def _generate(system: str, user: str, max_tokens: int,
              source: str, category: str, excerpt: str = "") -> str:
    """Run the LLM and record one telemetry event (best-effort)."""
    client = get_llm_client()
    raw = client.generate(system=system, user=user, max_tokens=max_tokens)
    telemetry.record(source, category, client.last_metrics or {}, excerpt)
    return raw


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

    category = telemetry.categorize(message)
    raw = _generate(system, user, 500, "chat", category, message.strip())
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

    scope = module.split(":")[-1]
    category = telemetry.categorize_scope(scope, ctx.get("module_name", ""))
    raw = _generate("You are a precise retail analytics summariser.", user,
                    300, "summarise", category,
                    excerpt=ctx.get("module_name", scope))
    safe, _ = guardrail.apply(raw, ctx, module=module, prompt=template)
    return safe


# ── Module 8c: multi-select integrated briefing ──────────────────────────────

def multi_summary(scopes: List[str]) -> str:
    if not scopes:
        return "Select at least one module to summarise.\n\n[Data-grounded]"
    ctx = context_builder.build_multi_context(scopes)
    template = load_prompt("multi_select_summary.txt")
    user = template.replace("{context_json}", json.dumps(ctx, indent=2))

    category = telemetry.categorize_scope("+".join(scopes), " ".join(scopes))
    raw = _generate("You are a precise retail analytics summariser.", user,
                    500, "multi", category, excerpt="+".join(scopes))
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
    raw = _generate("You are an expert retail analytics assistant.",
                    prompt_body, 600, "narrative",
                    telemetry.categorize_scope("module_7"),
                    excerpt="module_7_lift_narrative")
    safe, _ = guardrail.apply(raw, ctx, module="module_7", prompt=prompt_body)
    return safe
