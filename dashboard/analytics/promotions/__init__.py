"""
Promotion effectiveness analytics.

The promotion-lift model itself is trained offline in
`ml/promotions/promotion_lift_model.ipynb`. This package is the analytics
entry point that exposes its validated outputs (PromotionOutput contract)
to the dashboard via the shared PromotionLoader.

Consumed by:
- Module 3: Promotion Effectiveness (visualisation + AI narrative)
- Module 7: Promotion Lift Model (model diagnostics)
- Module 8: Chat Interface (grounding context for the LLM)
"""

from typing import Any, Dict, List

from dashboard.analytics.common.promotion_loader import get_promotion_loader


def analyze_promotion_effectiveness() -> Dict[str, Any]:
    """
    Return headline promotion-lift metrics + per-SKU summary.

    Reads the model output contract (no training here). Returns an empty
    structure if the notebook has not been run yet.
    """
    loader = get_promotion_loader()
    if not loader.available():
        return {"available": False, "metrics": {}, "by_sku": []}
    summary = loader.load_summary()
    return {
        "available": True,
        "metrics": loader.headline_metrics(),
        "by_sku": summary.to_dict(orient="records") if not summary.empty else [],
    }


def get_promotion_contract(sku_id: int = None) -> List[Dict[str, Any]]:
    """PromotionOutput rows as schema-validated dicts (Layer 2 payload)."""
    return get_promotion_loader().as_contract(sku_id)
