# AI-assisted: reviewed by team
"""Module 10 — Appendix & Export."""

from pathlib import Path

import gradio as gr

REPO_ROOT = Path(__file__).resolve().parents[2]


def _export_paths() -> list[tuple[str, Path]]:
    candidates = [
        ("Raw data", REPO_ROOT / "data" / "data_raw.csv"),
        ("Promotion output", REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs" / "promotion_output.csv"),
        ("SKU lift summary", REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs" / "sku_lift_summary.csv"),
        ("Forecast output", REPO_ROOT / "ml" / "ml_forecasting" / "outputs" / "forecast_output.csv"),
        ("Elasticity context", REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs" / "ai_context_module4.json"),
        ("Scenario context", REPO_ROOT / "dashboard" / "analytics" / "scenarios" / "outputs" / "ai_context_module5.json"),
        ("Requirements", REPO_ROOT / "requirements.txt"),
    ]
    return [(label, p) for label, p in candidates if p.exists()]


def build_appendix_export_tab():
    exports = _export_paths()

    with gr.Tab("10 · Export"):
        gr.Markdown("## Module 10 — Appendix & Export")
        gr.Markdown(
            "Methods, data dictionary, and downloadable artefacts. "
            "GitHub repo: see course submission link."
        )

        gr.Markdown("""
### Methods summary
| Module | Method |
|--------|--------|
| 3–7 Promotions | XGBoost counterfactual + matched control; bootstrap CIs |
| 4 Elasticity | Log-log OLS per SKU |
| 5 Scenarios | Constant-elasticity what-if |
| 6 Forecast | Linear trend on last 52 weeks (baseline) |

### Data dictionary
See **Module 2 — Data Explorer** for column definitions.

### Model constraints
- All models target **< 8 GB RAM**
- API keys via environment variables / GitHub Secrets only
        """)

        gr.Markdown("### Downloadable files")
        if not exports:
            gr.Markdown("_No export files found yet._")
        else:
            for label, path in exports:
                gr.DownloadButton(label=f"Download — {label}", value=str(path))

        gr.Markdown(f"### Repository\n`{REPO_ROOT}`")
