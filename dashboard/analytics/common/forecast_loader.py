"""
Data access layer: load model-output contracts (forecasting).

Reads the Forecast contract produced by `ml/ml_forecasting/forecasting.ipynb`
and validates it against `schemas.ForecastOutput`. This is a pure file
consumer — the dashboard never trains or runs the model (Layer 6 reading
Layer 4 output, per docs/tech_stack.md).
"""

import os
import logging
from typing import Optional, List, Dict, Any

import pandas as pd

from dashboard.analytics.common.schemas import ForecastOutput

logger = logging.getLogger(__name__)

CONTRACT_COLS = [
    "sku_id", "period", "y_true", "y_pred", "y_lower", "y_upper", "model_name",
]


class ForecastLoader:
    """
    Central access point for forecasting model outputs.

    Reads `ml/ml_forecasting/outputs/{forecast,per_sku_metrics,test_summary}.csv`
    and exposes contract-validated, cached frames for the dashboard.
    """

    def __init__(self, outputs_dir: str = None):
        if outputs_dir is None:
            # From dashboard/analytics/common/forecast_loader.py -> repo root
            project_root = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "../../.."
            ))
            outputs_dir = os.path.join(
                project_root, "ml", "ml_forecasting", "outputs"
            )
        self.outputs_dir = outputs_dir
        self.forecast_csv = os.path.join(outputs_dir, "forecast.csv")
        self.per_sku_csv = os.path.join(outputs_dir, "per_sku_metrics.csv")
        self.summary_csv = os.path.join(outputs_dir, "test_summary.csv")
        self._forecast: Optional[pd.DataFrame] = None
        self._per_sku: Optional[pd.DataFrame] = None
        self._summary: Optional[pd.DataFrame] = None

    def available(self) -> bool:
        """True if the forecast contract file exists (notebook has been run)."""
        return os.path.exists(self.forecast_csv)

    def load_forecast(self, force_reload: bool = False) -> pd.DataFrame:
        """Load + validate + cache the Forecast contract."""
        if self._forecast is not None and not force_reload:
            return self._forecast.copy()
        if not self.available():
            raise FileNotFoundError(
                f"Forecast contract not found: {self.forecast_csv}\n"
                f"Run ml/ml_forecasting/forecasting.ipynb to generate it."
            )
        df = pd.read_csv(self.forecast_csv)
        missing = set(CONTRACT_COLS) - set(df.columns)
        if missing:
            raise ValueError(
                f"Forecast file violates the contract, missing: {missing}"
            )
        df["period"] = pd.to_datetime(df["period"])
        df["sku_id"] = df["sku_id"].astype(int)
        df = df.sort_values(["sku_id", "period"]).reset_index(drop=True)
        self._forecast = df
        logger.info("Loaded forecast contract: %d rows", df.shape[0])
        return df.copy()

    def load_per_sku_metrics(self) -> pd.DataFrame:
        """Per-SKU test metrics (empty frame if not produced yet)."""
        if self._per_sku is None:
            self._per_sku = (
                pd.read_csv(self.per_sku_csv)
                if os.path.exists(self.per_sku_csv) else pd.DataFrame()
            )
        return self._per_sku.copy()

    def load_summary(self) -> Dict[str, Any]:
        """One-row overall test summary as a dict ({} if not produced yet)."""
        if self._summary is None:
            self._summary = (
                pd.read_csv(self.summary_csv)
                if os.path.exists(self.summary_csv) else pd.DataFrame()
            )
        if self._summary.empty:
            return {}
        return self._summary.iloc[0].to_dict()

    def get_sku_list(self) -> List[int]:
        return sorted(self.load_forecast()["sku_id"].unique().tolist())

    def get_sku_forecast(self, sku_id: int) -> pd.DataFrame:
        df = self.load_forecast()
        return df[df["sku_id"] == int(sku_id)].sort_values("period")

    def as_contract(self, sku_id: int = None) -> List[Dict[str, Any]]:
        """Rows as schema-validated ForecastOutput dicts (Layer 2 payload)."""
        df = (self.get_sku_forecast(sku_id) if sku_id is not None
              else self.load_forecast())
        return [
            ForecastOutput(
                sku_id=str(r.sku_id),
                period=str(pd.Timestamp(r.period).date()),
                y_true=None if pd.isna(r.y_true) else float(r.y_true),
                y_pred=float(r.y_pred),
                y_lower=float(r.y_lower),
                y_upper=float(r.y_upper),
                model_name=str(r.model_name),
            ).to_dict()
            for r in df.itertuples(index=False)
        ]


_forecast_loader: Optional[ForecastLoader] = None


def get_forecast_loader() -> ForecastLoader:
    """Get or create the singleton ForecastLoader instance."""
    global _forecast_loader
    if _forecast_loader is None:
        _forecast_loader = ForecastLoader()
    return _forecast_loader
