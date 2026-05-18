# Module 10 — Appendix & Export
# Owner: Dashboard
# Description: Method notes (KPI formulas + model specs) and one-click
#              downloads of every underlying dataset / model output.

from pathlib import Path

import gradio as gr

from dashboard.components import ui

ROOT = Path(__file__).resolve().parents[2]

EXPORTS = [
    ("Raw dataset", ROOT / "data" / "data_raw.csv"),
    ("Forecast (actual vs predicted + CI)",
     ROOT / "ml" / "ml_forecasting" / "outputs" / "forecast.csv"),
    ("Forecast — per-SKU metrics",
     ROOT / "ml" / "ml_forecasting" / "outputs" / "per_sku_metrics.csv"),
    ("Forecast — test summary",
     ROOT / "ml" / "ml_forecasting" / "outputs" / "test_summary.csv"),
    ("Promotion output (lift per SKU-week)",
     ROOT / "ml" / "promotions" / "promotion_output.csv"),
    ("Promotion — per-SKU lift summary",
     ROOT / "ml" / "promotions" / "sku_lift_summary.csv"),
    ("AI guardrail failure log",
     ROOT / "ai" / "services" / "failure_log.jsonl"),
]

METHOD_NOTES_MD = """
### Method notes

**KPI formulas (Module 1 / 2)**
- *Total revenue* = Σ (`demand_units` × `price`) over all rows.
- *Total demand* = Σ `demand_units`.
- *Average price* = mean of `price` across all rows.
- *Promotions* = count of rows where `feat_main_page` is true.

**Demand forecasting (Module 6)** — `HistGradientBoostingRegressor` on
`log1p(weekly_sales)` with lag / rolling / calendar / promo features.
Chronological panel split (13-week validation, 13-week test); 95% intervals
from residual quantiles. Metrics are on the held-out test weeks.

**Promotion lift (Modules 3 & 7)** — XGBoost (log1p target) with a
counterfactual + matched-control ensemble. Lift % = incremental ÷ baseline.
Out-of-sample metrics from 5-fold time-series CV.

**AI layer (Module 8)** — provider-agnostic client (free in-Space open model
by default). Context grounded in the above outputs; numeric guardrail +
enforced `[Data-grounded]` / `[General inference]` label.

**Reproducibility** — all outputs regenerate from the notebooks in `ml/`.
Contracts enforced by `dashboard/analytics/common/schemas.py`.
"""


def build_appendix_export_tab():
    """Render Module 10 inside a running gr.Blocks context."""
    with gr.Tab("10. Appendix & Export"):
        gr.HTML(ui.header(
            "Appendix & Export — Module 10",
            "Methodology reference and downloadable copies of every dataset "
            "and model output behind the dashboard."))

        gr.Markdown(METHOD_NOTES_MD)

        gr.Markdown("#### Downloads")
        for label, path in EXPORTS:
            if path.exists():
                size_kb = path.stat().st_size / 1024
                with gr.Row():
                    gr.Markdown(f"**{label}** · `{path.name}` "
                                f"({size_kb:,.0f} KB)")
                    gr.DownloadButton(f"⬇ {path.name}", value=str(path),
                                      size="sm")
            else:
                gr.Markdown(f"**{label}** · _not generated yet "
                            f"(`{path.name}`)_")


if __name__ == "__main__":
    with gr.Blocks(title="Appendix & Export") as demo:
        build_appendix_export_tab()
    demo.launch()
