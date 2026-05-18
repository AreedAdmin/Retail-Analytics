# AI-assisted: reviewed by [name]
"""
chart_summary_service — click-to-summarise for a single chart.

Mirror of chat_service but uses system_chart_summary.txt and
build_chart_context().  Output word cap is tighter (≤120 words).
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

_SYSTEM_PROMPT_ID = "system_chart_summary_v1"


def _load_prompt(filename: str) -> str:
    path: Path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def _extract_label(text: str) -> str:
    if "[Data-grounded]" in text:
        return "Data-grounded"
    if "[General inference]" in text:
        return "General inference"
    return "General inference"


def summarise_chart(chart_id: str, chart_data: dict | None = None) -> str:
    """
    Return a ≤120-word plain-English summary of the given chart.

    chart_data: live data from the chart click (optional).  If None,
    context is read from the registry.
    """
    session_id = uuid.uuid4().hex[:8]

    context = build_chart_context(chart_id, chart_data)
    if context is None:
        return "I don't have data on this chart yet.\n[General inference]"

    context_json = json.dumps(context, indent=2)
    template = _load_prompt("system_chart_summary.txt")
    system_prompt = template.replace("{context_json}", context_json)

    provider_name = "echo"
    model_name = "echo-v1"
    latency_ms = 0
    tokens_in = None
    tokens_out = None
    error_str = None
    raw_text = ""

    try:
        provider = get_provider()
        resp = provider.generate(system_prompt, f"Summarise chart: {chart_id}")
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
            user_query=f"chart_summary:{chart_id}",
            context_modules=[context.get("module_name", chart_id)],
            provider=provider_name, model=model_name,
            system_prompt_id=_SYSTEM_PROMPT_ID,
            latency_ms=0, tokens_in=None, tokens_out=None,
            answer_label="n/a", answer_text=result,
            guardrail_input={"allowed": True, "reason": None},
            guardrail_output={"unverified_numbers": [], "label_auto_added": False, "system_leak_redacted": False},
            refusal_reason="provider_down", error=error_str,
        )
        return result

    clean_text, flags = validate_output(raw_text, context)
    label = _extract_label(clean_text)

    log_interaction(
        session_id=session_id, event_type="chart_summary",
        user_query=f"chart_summary:{chart_id}",
        context_modules=[context.get("module_name", chart_id)],
        provider=provider_name, model=model_name,
        system_prompt_id=_SYSTEM_PROMPT_ID,
        latency_ms=latency_ms, tokens_in=tokens_in, tokens_out=tokens_out,
        answer_label=label, answer_text=clean_text,
        guardrail_input={"allowed": True, "reason": None},
        guardrail_output=flags,
    )
    return clean_text
