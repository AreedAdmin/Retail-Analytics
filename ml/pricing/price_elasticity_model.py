"""
Module 4 — Price Elasticity model (offline trainer)
===================================================
Per-SKU log–log OLS regression:

    log(demand_units) = a + b·log(price) + c·promo_flag + e
    elasticity (own-price) = b

Run offline (the dashboard never trains — it reads the CSV output):

    python ml/pricing/price_elasticity_model.py

Writes the ElasticityOutput contract to ml/pricing/elasticity_output.csv
(see dashboard/analytics/common/schemas.py::ElasticityOutput).

Caveats (surfaced in Module 4 / Module 9): observational data → price
endogeneity; promo weeks are controlled for but not a clean experiment;
β is descriptive, not strictly causal.
"""

from __future__ import annotations

import os
import sys
import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
OUT_DIR = os.path.join(REPO_ROOT, "ml", "pricing")
OUT_CSV = os.path.join(OUT_DIR, "elasticity_output.csv")

MODEL_TYPE = "log_log_ols"
MIN_OBS = 12          # minimum weeks to fit a SKU
LOW_EVIDENCE_R2 = 0.05  # flag weak fits


def _load() -> pd.DataFrame:
    from dashboard.analytics.common.data_loader import get_data_loader

    df = get_data_loader().get_normalized_data()
    # log requires strictly positive demand & price
    df = df[(df["demand_units"] > 0) & (df["price"] > 0)].copy()
    df["log_demand"] = np.log(df["demand_units"])
    df["log_price"] = np.log(df["price"])
    df["promo"] = df["feat_main_page"].astype(float)
    return df


def fit_sku(g: pd.DataFrame) -> dict:
    """Fit one SKU; return an ElasticityOutput row (+ diagnostics)."""
    n = len(g)
    base = {
        "model_type": MODEL_TYPE,
        "n_obs": int(n),
        "r_squared": np.nan,
        "low_evidence": True,
        "elasticity_value": np.nan,
        "confidence_low": np.nan,
        "confidence_high": np.nan,
    }
    if n < MIN_OBS or g["log_price"].std() < 1e-6:
        return base

    X = sm.add_constant(g[["log_price", "promo"]])
    try:
        res = sm.OLS(g["log_demand"], X).fit()
    except Exception as e:  # pragma: no cover - defensive
        log.warning("OLS failed for a SKU: %s", e)
        return base

    beta = float(res.params["log_price"])
    ci = res.conf_int(alpha=0.05).loc["log_price"]
    r2 = float(res.rsquared)
    return {
        "model_type": MODEL_TYPE,
        "n_obs": int(n),
        "r_squared": round(r2, 4),
        "low_evidence": bool(r2 < LOW_EVIDENCE_R2),
        "elasticity_value": round(beta, 4),
        "confidence_low": round(float(ci[0]), 4),
        "confidence_high": round(float(ci[1]), 4),
    }


def build() -> pd.DataFrame:
    df = _load()
    rows = []
    for sku_id, g in df.groupby("sku_id"):
        r = fit_sku(g)
        r["sku_id"] = int(sku_id)
        rows.append(r)

    out = pd.DataFrame(rows)[[
        "sku_id", "elasticity_value", "confidence_low", "confidence_high",
        "model_type", "n_obs", "r_squared", "low_evidence",
    ]].sort_values("sku_id").reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    fitted = out["elasticity_value"].dropna()
    elastic = int((fitted < -1).sum())
    inelastic = int((fitted.between(-1, 0, inclusive="left")).sum())
    log.info("Wrote %s", OUT_CSV)
    log.info(
        "SKUs fitted: %d/%d | median elasticity %.2f | "
        "elastic %d, inelastic %d, low-evidence %d",
        fitted.size, len(out),
        float(fitted.median()) if fitted.size else float("nan"),
        elastic, inelastic, int(out["low_evidence"].sum()),
    )
    return out


if __name__ == "__main__":
    build()
