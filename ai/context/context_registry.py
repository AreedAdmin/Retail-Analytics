# AI-assisted: reviewed by [name]
"""
Context registry — maps chart_id to a prioritised list of candidate paths.

resolve_context_path() returns the first existing path, or None if none found.
Using a candidate list makes the registry resilient to ML team renames.
"""
from pathlib import Path

from ai.config.settings import REPO_ROOT

# Each key maps to an ordered list of candidate paths (first match wins).
CHART_CONTEXT_CANDIDATES: dict[str, list[Path]] = {
    "module7_lift_summary": [
        REPO_ROOT / "ml/ml_promotions_pricing/outputs/ai_context_module7.json",
        REPO_ROOT / "ml/promotions/outputs/ai_context_module7.json",        # legacy path
    ],
    "module6_forecast": [
        REPO_ROOT / "ml/ml_forecasting/outputs/ai_context_module6.json",
    ],
    "module4_elasticity": [
        REPO_ROOT / "ml/ml_promotions_pricing/outputs/ai_context_module4.json",
        REPO_ROOT / "ml/promotions/outputs/ai_context_module4.json",        # legacy
    ],
    "module5_scenarios": [
        REPO_ROOT / "dashboard/analytics/scenarios/outputs/ai_context_module5.json",
    ],
}

# Human-readable module names keyed by chart_id (used in context_builder keys).
CHART_MODULE_NAMES: dict[str, str] = {
    "module7_lift_summary": "module_7_promotion_lift",
    "module6_forecast":     "module_6_demand_forecast",
    "module4_elasticity":   "module_4_price_elasticity",
    "module5_scenarios":    "module_5_scenarios",
}


def resolve_context_path(chart_id: str) -> Path | None:
    """Return the first existing path for chart_id, or None if none exist."""
    for candidate in CHART_CONTEXT_CANDIDATES.get(chart_id, []):
        if candidate.exists():
            return candidate
    return None
