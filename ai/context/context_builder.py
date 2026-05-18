# AI-assisted: reviewed by [name]
"""
Context builder — reads ML/analytics output JSON files and packages
them for the LLM.  Never touches data/data_raw.csv.
"""
import json

from .context_registry import (
    CHART_CONTEXT_CANDIDATES,
    CHART_MODULE_NAMES,
    resolve_context_path,
)


def build_chat_context(modules: list[str] | None = None) -> dict:
    """
    Read every available ai_context_*.json from the registry.

    Returns a dict keyed by human-readable module name:
        {"module_7_promotion_lift": {...}, ...}
    A "_missing" key lists chart_ids where no file was found.
    """
    result: dict = {}
    missing: list[str] = []

    chart_ids = list(CHART_CONTEXT_CANDIDATES.keys())

    for chart_id in chart_ids:
        module_name = CHART_MODULE_NAMES.get(chart_id, chart_id)
        # If caller wants specific modules, skip others.
        if modules and module_name not in modules:
            continue
        path = resolve_context_path(chart_id)
        if path is None:
            missing.append(chart_id)
            continue
        try:
            with open(path, encoding="utf-8") as f:
                result[module_name] = json.load(f)
        except (OSError, json.JSONDecodeError):
            missing.append(chart_id)

    if missing:
        result["_missing"] = missing
    return result


def build_chart_context(chart_id: str, chart_data: dict | None = None) -> dict:
    """
    Build context for a single chart.

    If chart_data is provided (live chart click), use it directly.
    Otherwise read from the registry.  Always wraps in the
    AIContextPayload contract: {module_name, chart_id, metrics, key_findings}.
    Returns None only if no data source is available.
    """
    module_name = CHART_MODULE_NAMES.get(chart_id, chart_id)

    if chart_data is not None:
        # Caller supplied live data — wrap it in the contract shape.
        return {
            "module_name":   module_name,
            "chart_id":      chart_id,
            "metrics":       chart_data.get("metrics", chart_data),
            "key_findings":  chart_data.get("key_findings", []),
        }

    path = resolve_context_path(chart_id)
    if path is None:
        return None  # type: ignore[return-value]

    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None  # type: ignore[return-value]

    return {
        "module_name":  raw.get("module_name", module_name),
        "chart_id":     raw.get("chart_id", chart_id),
        "metrics":      raw.get("metrics", {}),
        "key_findings": raw.get("key_findings", []),
    }
