# AI-assisted: reviewed by [name]
"""
multi_chart_service — synthesise multiple selected charts into one narrative.
"""
import json
import logging
import uuid
from pathlib import Path

from ai.config.settings import PROMPTS_DIR
from ai.context.context_builder import build_chart_context
from ai.guardrails.output_validator import validate_output
from ai.guardrails.refusal_messages import get_refusal
from ai.logs.interaction_logger import log_interaction
from ai.providers import get_provider
from ai.providers.base import LlmProviderError

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT_ID = "system_multi_summary_v1"


def _load_prompt(filename: str) -> str:
    path: Path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def _extract_label(text: str) -> str:
    if "[Data-grounded]" in text:
        return "Data-grounded"
    if "[General inference]" in text:
        return "General inference"
    return "General inference"


def summarise_selection(chart_ids: list[str]) -> str:
    """
    Load each chart's context, concatenate, generate one synthesis paragraph.
    """
    session_id = uuid.uuid4().hex[:8]

    contexts: dict[str, dict] = {}
    for cid in chart_ids:
        ctx = build_chart_context(cid)
        if ctx is not None:
            contexts[cid] = ctx

    if not contexts:
        return "I don't have data on any of the selected charts yet.\n[General inference]"

    combined_context = {"charts": contexts}
    context_json = json.dumps(combined_context, indent=2)

    template = _load_prompt("system_multi_summary.txt")
    system_prompt = template.replace("{context_json}", context_json)

    modules = [ctx.get("module_name", cid) for cid, ctx in contexts.items()]
    provider_name = "echo"
    model_name = "echo-v1"
    latency_ms = 0
    tokens_in = None
    tokens_out = None
    error_str = None
    raw_text = ""

    try:
        provider = get_provider()
        resp = provider.generate(
            system_prompt,
            f"Synthesise the selected charts: {', '.join(chart_ids)}"
        )
        raw_text = resp.text
        provider_name = resp.provider
        model_name = resp.model
        latency_ms = resp.latency_ms
        tokens_in = resp.tokens_in
        tokens_out = resp.tokens_out
    except LlmProviderError as exc:
        error_str = str(exc)
        result = get_refusal("provider_down")
        log_interaction(
            session_id=session_id, event_type="error",
            user_query=f"multi_summary:{chart_ids}",
            context_modules=modules,
            provider=provider_name, model=model_name,
            system_prompt_id=_SYSTEM_PROMPT_ID,
            latency_ms=0, tokens_in=None, tokens_out=None,
            answer_label="n/a", answer_text=result,
            guardrail_input={"allowed": True, "reason": None},
            guardrail_output={"unverified_numbers": [], "label_auto_added": False, "system_leak_redacted": False},
            refusal_reason="provider_down", error=error_str,
        )
        return result

    clean_text, flags = validate_output(raw_text, combined_context)
    label = _extract_label(clean_text)

    log_interaction(
        session_id=session_id, event_type="multi_summary",
        user_query=f"multi_summary:{chart_ids}",
        context_modules=modules,
        provider=provider_name, model=model_name,
        system_prompt_id=_SYSTEM_PROMPT_ID,
        latency_ms=latency_ms, tokens_in=tokens_in, tokens_out=tokens_out,
        answer_label=label, answer_text=clean_text,
        guardrail_input={"allowed": True, "reason": None},
        guardrail_output=flags,
    )
    return clean_text
