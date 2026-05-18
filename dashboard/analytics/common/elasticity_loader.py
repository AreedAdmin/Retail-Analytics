"""
Data access layer: load model-output contracts (price elasticity).

Reads the Elasticity contract produced by
`ml/pricing/price_elasticity_model.py` and validates it against
`schemas.ElasticityOutput`. Pure file consumer — the dashboard never
fits the regression (Layer 6 reading Layer 4 output).
"""

import os
import logging
from typing import Optional, List, Dict, Any

import pandas as pd

from dashboard.analytics.common.schemas import ElasticityOutput

logger = logging.getLogger(__name__)

CONTRACT_COLS = [
    "sku_id", "elasticity_value", "confidence_low", "confidence_high",
    "model_type",
]


class ElasticityLoader:
    """Central access point for the price-elasticity model output."""

    def __init__(self, pricing_dir: str = None):
        if pricing_dir is None:
            project_root = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "../../.."
            ))
            pricing_dir = os.path.join(project_root, "ml", "pricing")
        self.pricing_dir = pricing_dir
        self.output_csv = os.path.join(pricing_dir, "elasticity_output.csv")
        self._df: Optional[pd.DataFrame] = None

    def available(self) -> bool:
        return os.path.exists(self.output_csv)

    def load(self, force_reload: bool = False) -> pd.DataFrame:
        """Load + validate + cache the Elasticity contract."""
        if self._df is not None and not force_reload:
            return self._df.copy()
        if not self.available():
            raise FileNotFoundError(
                f"Elasticity contract not found: {self.output_csv}\n"
                f"Run: python ml/pricing/price_elasticity_model.py"
            )
        df = pd.read_csv(self.output_csv)
        missing = set(CONTRACT_COLS) - set(df.columns)
        if missing:
            raise ValueError(
                f"Elasticity file violates the contract, missing: {missing}"
            )
        df["sku_id"] = df["sku_id"].astype(int)
        self._df = df.sort_values("sku_id").reset_index(drop=True)
        logger.info("Loaded elasticity contract: %d SKUs", len(self._df))
        return self._df.copy()

    def get_sku_list(self) -> List[int]:
        df = self.load()
        return sorted(df.loc[df["elasticity_value"].notna(), "sku_id"]
                      .astype(int).tolist())

    def get_elasticity(self, sku_id: int) -> Optional[float]:
        df = self.load()
        row = df[df["sku_id"] == int(sku_id)]
        if row.empty:
            return None
        v = row.iloc[0]["elasticity_value"]
        return None if pd.isna(v) else float(v)

    def headline_metrics(self) -> Dict[str, Any]:
        df = self.load()
        fitted = df["elasticity_value"].dropna()
        if fitted.empty:
            return {}
        return {
            "num_skus": int(df["sku_id"].nunique()),
            "num_fitted": int(fitted.size),
            "median_elasticity": round(float(fitted.median()), 3),
            "num_elastic": int((fitted < -1).sum()),
            "num_inelastic": int(fitted.between(-1, 0, inclusive="left").sum()),
            "num_low_evidence": int(df.get("low_evidence",
                                            pd.Series(dtype=bool)).sum()),
        }

    def classify(self) -> pd.DataFrame:
        """Add a human-readable elasticity class column."""
        df = self.load()

        def _cls(v):
            if pd.isna(v):
                return "unfitted"
            if v < -1:
                return "elastic"
            if v < 0:
                return "inelastic"
            return "atypical (≥0)"

        df = df.copy()
        df["class"] = df["elasticity_value"].apply(_cls)
        return df

    def as_contract(self) -> List[Dict[str, Any]]:
        """Rows as schema-validated ElasticityOutput dicts (Layer 2 payload)."""
        df = self.load()
        return [
            ElasticityOutput(
                sku_id=str(r.sku_id),
                elasticity_value=(None if pd.isna(r.elasticity_value)
                                  else float(r.elasticity_value)),
                confidence_low=(None if pd.isna(r.confidence_low)
                                else float(r.confidence_low)),
                confidence_high=(None if pd.isna(r.confidence_high)
                                 else float(r.confidence_high)),
                model_type=str(r.model_type),
            ).to_dict()
            for r in df.itertuples(index=False)
        ]


_elasticity_loader: Optional[ElasticityLoader] = None


def get_elasticity_loader() -> ElasticityLoader:
    """Get or create the singleton ElasticityLoader instance."""
    global _elasticity_loader
    if _elasticity_loader is None:
        _elasticity_loader = ElasticityLoader()
    return _elasticity_loader
