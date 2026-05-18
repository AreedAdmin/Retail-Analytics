# AI-assisted: reviewed by team
"""Lightweight demand forecasting (baseline for Module 6 until ML outputs land)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS_DIR = REPO_ROOT / "ml" / "ml_forecasting" / "outputs"
FORECAST_CSV = OUTPUTS_DIR / "forecast_output.csv"
CONTEXT_PATH = OUTPUTS_DIR / "ai_context_module6.json"

HORIZON = 4
TRAIN_WEEKS = 52


def _forecast_sku(grp: pd.DataFrame, horizon: int = HORIZON) -> pd.DataFrame:
    grp = grp.sort_values("period")
    train = grp.tail(TRAIN_WEEKS)
    if len(train) < 8:
        return pd.DataFrame()

    x = train["period"].values.reshape(-1, 1)
    y = train["demand_units"].values
    model = LinearRegression().fit(x, y)
    last_period = int(train["period"].max())
    future_periods = list(range(last_period + 1, last_period + horizon + 1))
    preds = model.predict(np.array(future_periods).reshape(-1, 1))
    resid_std = float(np.std(y - model.predict(x)))
    rows = []
    sku_id = int(train["sku_id"].iloc[0])
    for i, period in enumerate(future_periods):
        pred = max(0.0, float(preds[i]))
        rows.append({
            "sku_id": sku_id,
            "period": period,
            "y_true": None,
            "y_pred": round(pred, 2),
            "y_lower": round(max(0, pred - 1.28 * resid_std), 2),
            "y_upper": round(pred + 1.28 * resid_std, 2),
            "model_name": "linear_trend_baseline",
        })
    return pd.DataFrame(rows)


def compute_forecasts(df: pd.DataFrame, horizon: int = HORIZON) -> pd.DataFrame:
    parts = [_forecast_sku(grp, horizon) for _, grp in df.groupby("sku_id")]
    parts = [p for p in parts if not p.empty]
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def evaluate_holdout(df: pd.DataFrame, holdout: int = 8) -> dict:
    """Simple holdout MAPE across SKUs."""
    errors = []
    for _, grp in df.groupby("sku_id"):
        grp = grp.sort_values("period")
        if len(grp) <= holdout + 8:
            continue
        train = grp.iloc[:-holdout]
        test = grp.iloc[-holdout:]
        x = train["period"].values.reshape(-1, 1)
        y = train["demand_units"].values
        model = LinearRegression().fit(x, y)
        pred = model.predict(test["period"].values.reshape(-1, 1))
        actual = test["demand_units"].values
        mask = actual > 0
        if mask.any():
            mape = np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask])) * 100
            errors.append(mape)
    if not errors:
        return {"mape_pct": None, "rmse": None}
    return {
        "mape_pct": round(float(np.mean(errors)), 2),
        "rmse": None,
    }


def write_forecast_outputs(df: pd.DataFrame) -> pd.DataFrame:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    forecast_df = compute_forecasts(df)
    if forecast_df.empty:
        return forecast_df
    forecast_df.to_csv(FORECAST_CSV, index=False)
    metrics = evaluate_holdout(df)
    declining = []
    for sku_id, grp in df.groupby("sku_id"):
        recent = grp.sort_values("period").tail(8)["demand_units"].mean()
        prior = grp.sort_values("period").iloc[-16:-8]["demand_units"].mean()
        if prior > 0 and (recent - prior) / prior < -0.1:
            declining.append(int(sku_id))
    payload = {
        "module_name": "module_6_demand_forecast",
        "chart_id": "forecast_summary",
        "metrics": {
            "horizon_weeks": HORIZON,
            "num_skus_forecast": int(forecast_df["sku_id"].nunique()),
            "holdout_mape_pct": metrics.get("mape_pct"),
            "model_name": "linear_trend_baseline",
        },
        "key_findings": [
            f"Forecasts generated for {forecast_df['sku_id'].nunique()} SKUs over {HORIZON} weeks",
            f"Holdout MAPE (8-week): {metrics.get('mape_pct')}%",
            f"SKUs with declining recent demand: {declining[:10]}",
        ],
    }
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return forecast_df
