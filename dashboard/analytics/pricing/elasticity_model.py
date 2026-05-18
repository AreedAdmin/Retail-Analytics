# AI-assisted: reviewed by team
"""Log-log price elasticity estimation per SKU."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS_DIR = REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs"
CONTEXT_PATH = OUTPUTS_DIR / "ai_context_module4.json"


def estimate_elasticity(df: pd.DataFrame, min_obs: int = 20) -> pd.DataFrame:
    """
    Estimate price elasticity per SKU via log-log OLS: log(demand) ~ log(price).
    Returns ElasticityOutput-shaped DataFrame.
    """
    rows = []
    for sku_id, grp in df.groupby("sku_id"):
        sub = grp[(grp["demand_units"] > 0) & (grp["price"] > 0)].copy()
        if len(sub) < min_obs:
            continue
        x = np.log(sub["price"].values).reshape(-1, 1)
        y = np.log(sub["demand_units"].values)
        model = LinearRegression().fit(x, y)
        coef = float(model.coef_[0])
        resid = y - model.predict(x)
        se = float(np.std(resid) / max(np.sqrt(len(sub)), 1))
        rows.append({
            "sku_id": int(sku_id),
            "elasticity_value": round(coef, 3),
            "confidence_low": round(coef - 1.96 * se, 3),
            "confidence_high": round(coef + 1.96 * se, 3),
            "model_type": "log_log_regression",
            "n_obs": len(sub),
            "r2": round(float(model.score(x, y)), 3),
        })
    if not rows:
        return pd.DataFrame(
            columns=[
                "sku_id", "elasticity_value", "confidence_low",
                "confidence_high", "model_type", "n_obs", "r2",
            ]
        )
    return pd.DataFrame(rows).sort_values("elasticity_value")


def write_elasticity_context(elasticity_df: pd.DataFrame) -> None:
    """Persist AI context JSON for Module 4 and chat."""
    if elasticity_df.empty:
        return
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    elastic = elasticity_df[elasticity_df["elasticity_value"] < -1]
    inelastic = elasticity_df[elasticity_df["elasticity_value"] >= -1]
    top = elasticity_df.nsmallest(5, "elasticity_value")
    bottom = elasticity_df.nlargest(5, "elasticity_value")
    payload = {
        "module_name": "module_4_price_elasticity",
        "chart_id": "elasticity_summary",
        "metrics": {
            "num_skus": int(len(elasticity_df)),
            "avg_elasticity": round(float(elasticity_df["elasticity_value"].mean()), 3),
            "median_elasticity": round(float(elasticity_df["elasticity_value"].median()), 3),
            "num_elastic_skus": int(len(elastic)),
            "num_inelastic_skus": int(len(inelastic)),
        },
        "key_findings": [
            f"{len(elastic)} SKUs are price-elastic (elasticity < -1)",
            f"{len(inelastic)} SKUs are relatively inelastic",
            f"Most elastic SKU: {int(top.iloc[0]['sku_id'])} "
            f"(elasticity {top.iloc[0]['elasticity_value']})",
            f"Least elastic SKU: {int(bottom.iloc[0]['sku_id'])} "
            f"(elasticity {bottom.iloc[0]['elasticity_value']})",
        ],
    }
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def get_or_compute_elasticity(df: pd.DataFrame) -> pd.DataFrame:
    """Compute elasticity and refresh AI context file."""
    elasticity_df = estimate_elasticity(df)
    write_elasticity_context(elasticity_df)
    return elasticity_df
