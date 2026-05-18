# AI-assisted: reviewed by team
"""Load promotion lift outputs from the ML pipeline."""

from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS_DIR = REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs"


def load_sku_lift_summary() -> pd.DataFrame | None:
    path = OUTPUTS_DIR / "sku_lift_summary.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


def load_promotion_output() -> pd.DataFrame | None:
    path = OUTPUTS_DIR / "promotion_output.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, parse_dates=["period"])
    return df
