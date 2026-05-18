"""
Data access layer: load model-output contracts (promotion lift).

Reads the Promotion contract produced by
`ml/promotions/promotion_lift_model.ipynb` and validates it against
`schemas.PromotionOutput`. Pure file consumer — the dashboard never
trains or runs the model (Layer 6 reading Layer 4 output).

Files consumed:
    ml/promotions/promotion_output.csv   (PromotionOutput contract)
    ml/promotions/sku_lift_summary.csv   (per-SKU aggregates + CI)
    ml/promotions/ai_context_module7.json (model diagnostics for Module 7)
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any

import pandas as pd

from dashboard.analytics.common.schemas import PromotionOutput

logger = logging.getLogger(__name__)

CONTRACT_COLS = [
    "sku_id", "period", "promotion_flag", "incremental_sales", "lift_pct",
]


class PromotionLoader:
    """Central access point for promotion-lift model outputs."""

    def __init__(self, promo_dir: str = None):
        if promo_dir is None:
            project_root = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "../../.."
            ))
            promo_dir = os.path.join(project_root, "ml", "promotions")
        self.promo_dir = promo_dir
        self.output_csv = os.path.join(promo_dir, "promotion_output.csv")
        self.summary_csv = os.path.join(promo_dir, "sku_lift_summary.csv")
        self.context_json = os.path.join(promo_dir, "ai_context_module7.json")
        self._output: Optional[pd.DataFrame] = None
        self._summary: Optional[pd.DataFrame] = None

    def available(self) -> bool:
        """True if the promotion contract file exists."""
        return os.path.exists(self.output_csv)

    def load_output(self, force_reload: bool = False) -> pd.DataFrame:
        """Load + validate + cache the Promotion contract."""
        if self._output is not None and not force_reload:
            return self._output.copy()
        if not self.available():
            raise FileNotFoundError(
                f"Promotion contract not found: {self.output_csv}\n"
                f"Run ml/promotions/promotion_lift_model.ipynb to generate it."
            )
        df = pd.read_csv(self.output_csv)
        missing = set(CONTRACT_COLS) - set(df.columns)
        if missing:
            raise ValueError(
                f"Promotion file violates the contract, missing: {missing}"
            )
        df["period"] = pd.to_datetime(df["period"])
        df["sku_id"] = df["sku_id"].astype(int)
        df = df.sort_values(["sku_id", "period"]).reset_index(drop=True)
        self._output = df
        logger.info("Loaded promotion contract: %d rows", df.shape[0])
        return df.copy()

    def load_summary(self) -> pd.DataFrame:
        """Per-SKU lift summary (empty frame if not produced yet)."""
        if self._summary is None:
            self._summary = (
                pd.read_csv(self.summary_csv)
                if os.path.exists(self.summary_csv) else pd.DataFrame()
            )
            if not self._summary.empty:
                self._summary["sku_id"] = self._summary["sku_id"].astype(int)
        return self._summary.copy()

    def load_context(self) -> Dict[str, Any]:
        """Model-diagnostics JSON for Module 7 ({} if missing)."""
        if not os.path.exists(self.context_json):
            return {}
        try:
            return json.loads(open(self.context_json).read())
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("Could not parse %s: %s", self.context_json, e)
            return {}

    def headline_metrics(self) -> Dict[str, Any]:
        """Compact KPIs for the Module 3 header."""
        s = self.load_summary()
        if s.empty:
            return {}
        return {
            "num_skus": int(s["sku_id"].nunique()),
            "median_lift_pct": round(float(s["mean_lift_pct"].median()), 2),
            "max_lift_pct": round(float(s["mean_lift_pct"].max()), 2),
            "total_incremental_sales": round(
                float((s["mean_incremental_sales"] * s["n_promo_weeks"]).sum()), 1
            ),
            "total_promo_weeks": int(s["n_promo_weeks"].sum()),
        }

    def get_sku_list(self) -> List[int]:
        return sorted(self.load_output()["sku_id"].unique().tolist())

    def get_sku_output(self, sku_id: int) -> pd.DataFrame:
        df = self.load_output()
        return df[df["sku_id"] == int(sku_id)].sort_values("period")

    def as_contract(self, sku_id: int = None) -> List[Dict[str, Any]]:
        """Rows as schema-validated PromotionOutput dicts (Layer 2 payload)."""
        df = (self.get_sku_output(sku_id) if sku_id is not None
              else self.load_output())
        return [
            PromotionOutput(
                sku_id=str(r.sku_id),
                period=str(pd.Timestamp(r.period).date()),
                promotion_flag=bool(r.promotion_flag),
                incremental_sales=float(r.incremental_sales),
                lift_pct=float(r.lift_pct),
            ).to_dict()
            for r in df.itertuples(index=False)
        ]


_promotion_loader: Optional[PromotionLoader] = None


def get_promotion_loader() -> PromotionLoader:
    """Get or create the singleton PromotionLoader instance."""
    global _promotion_loader
    if _promotion_loader is None:
        _promotion_loader = PromotionLoader()
    return _promotion_loader
