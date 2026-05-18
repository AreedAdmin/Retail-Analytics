"""
Price elasticity analytics.

The elasticity regression itself is fit offline in
`ml/pricing/price_elasticity_model.py`. This package exposes its validated
output (ElasticityOutput contract) to the dashboard via ElasticityLoader,
and provides the price→demand→revenue projection used by the Scenario
Simulator (Module 5).

Consumed by:
- Module 4: Price Elasticity (visualisation + AI narrative)
- Module 5: Scenario Simulator (what-if analysis)
- Module 8: Chat Interface (grounding context for the LLM)
"""

from typing import Any, Dict, List

from dashboard.analytics.common.elasticity_loader import get_elasticity_loader


def estimate_price_elasticity() -> Dict[str, Any]:
    """Headline elasticity metrics + per-SKU classification (no fitting)."""
    loader = get_elasticity_loader()
    if not loader.available():
        return {"available": False, "metrics": {}, "by_sku": []}
    cls = loader.classify()
    return {
        "available": True,
        "metrics": loader.headline_metrics(),
        "by_sku": cls.to_dict(orient="records"),
    }


def get_elasticity_contract() -> List[Dict[str, Any]]:
    """ElasticityOutput rows as schema-validated dicts (Layer 2 payload)."""
    return get_elasticity_loader().as_contract()


def project_price_change(
    elasticity: float,
    baseline_demand: float,
    baseline_price: float,
    price_change_pct: float,
) -> Dict[str, float]:
    """
    Constant-elasticity projection of a price move (used by Module 5).

        demand_change_% ≈ elasticity · price_change_%
        revenue_change_% = (1+price_change_%)·(1+demand_change_%) − 1

    Percentages are in PERCENT units (e.g. +10.0 means +10%).
    """
    dp = price_change_pct / 100.0
    dd = elasticity * dp                       # fractional demand change
    new_demand = max(baseline_demand * (1 + dd), 0.0)
    new_price = baseline_price * (1 + dp)
    base_rev = baseline_demand * baseline_price
    new_rev = new_demand * new_price
    rev_change = (new_rev / base_rev - 1) if base_rev > 0 else 0.0
    return {
        "price_change_pct": round(price_change_pct, 2),
        "demand_change_pct": round(dd * 100, 2),
        "revenue_change_pct": round(rev_change * 100, 2),
        "baseline_demand": round(baseline_demand, 2),
        "new_demand": round(new_demand, 2),
        "baseline_price": round(baseline_price, 2),
        "new_price": round(new_price, 2),
        "baseline_revenue": round(base_rev, 2),
        "new_revenue": round(new_rev, 2),
    }
