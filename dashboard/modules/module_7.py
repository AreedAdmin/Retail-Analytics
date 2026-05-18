# AI-assisted: reviewed by [name]
"""
Module 7 — Promotion Lift Model Dashboard Tab
==============================================
Gradio UI component for the promotion lift model.
Displays model architecture, OOS metrics, lift charts,
heatmap, SKU drill-down, exportable table,
and AI-generated narrative with click-to-summarise.

Imports from:
  ml/promotions/outputs/promotion_output.csv   — contract output
  ml/promotions/outputs/sku_lift_summary.csv   — SKU summary
  ml/promotions/outputs/ai_context_module7.json — AI context
  ai/services/module7_ai_narrative.py           — AI narrative service
"""

import sys
import json
import pandas as pd
import gradio as gr
import plotly.graph_objects as go
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────

REPO_ROOT    = Path(__file__).resolve().parents[2]
OUTPUTS_PATH = REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs"
CONTEXT_PATH = OUTPUTS_PATH / "ai_context_module7.json"

sys.path.insert(0, str(REPO_ROOT))


# ── Load pre-computed outputs ─────────────────────────────────────────────────

def load_outputs():
    try:
        lift_df     = pd.read_csv(OUTPUTS_PATH / "promotion_output.csv", parse_dates=["period"])
        sku_summary = pd.read_csv(OUTPUTS_PATH / "sku_lift_summary.csv")
        with open(CONTEXT_PATH) as f:
            ai_context = json.load(f)
        return lift_df, sku_summary, ai_context, None
    except FileNotFoundError as e:
        return None, None, None, str(e)


# ── Chart builders ─────────────────────────────────────────────────────────────

def build_metrics_panel(ai_context: dict) -> go.Figure:
    """OOS performance metrics — 4 KPI cards."""
    m = ai_context["metrics"]
    labels = ["MAE", "RMSE", "sMAPE %", "R²"]
    values = [
        round(m["oos_mae"], 2),
        round(m["oos_rmse"], 2),
        round(m["oos_smape_pct"], 2),
        round(m["oos_r2"], 3),
    ]
    colors = ["#3498db", "#e67e22", "#e74c3c", "#2ecc71"]

    fig = go.Figure()
    for i, (label, value, color) in enumerate(zip(labels, values, colors)):
        fig.add_trace(go.Indicator(
            mode  = "number",
            value = value,
            title = {"text": label, "font": {"size": 14}},
            number= {"font": {"size": 32, "color": color}},
            domain= {"row": 0, "column": i},
        ))
    fig.update_layout(
        grid          = {"rows": 1, "columns": 4},
        height        = 160,
        margin        = dict(t=40, b=10, l=10, r=10),
        paper_bgcolor = "white",
        title         = (
            f"Fig 1 — OOS Metrics (5-fold TimeSeriesSplit CV) | "
            f"MAE={m['oos_mae']} | RMSE={m['oos_rmse']} | "
            f"sMAPE={m['oos_smape_pct']}% | R²={m['oos_r2']}"
        ),
    )
    return fig


def build_lift_bar(sku_summary: pd.DataFrame) -> go.Figure:
    """Incremental sales per SKU with 90% bootstrap CI."""
    s = sku_summary.sort_values("mean_incremental_sales", ascending=False)
    fig = go.Figure(go.Bar(
        x       = s["sku_id"].astype(str),
        y       = s["mean_incremental_sales"],
        error_y = dict(
            type       = "data",
            symmetric  = False,
            array      = (s["confidence_high"] - s["mean_incremental_sales"]).clip(lower=0),
            arrayminus = (s["mean_incremental_sales"] - s["confidence_low"]).clip(lower=0),
        ),
        marker  = dict(
            color      = s["mean_incremental_sales"],
            colorscale = "Blues",
            showscale  = True,
            colorbar   = dict(title="Incr. Units"),
        ),
        text         = s["mean_incremental_sales"].round(1).astype(str),
        textposition = "outside",
    ))
    fig.update_layout(
        title         = "Fig 2 — Mean Incremental Sales per SKU (90% Bootstrap CI)",
        xaxis_title   = "SKU ID",
        yaxis_title   = "Incremental Units (weekly avg)",
        height        = 440,
        paper_bgcolor = "white",
        plot_bgcolor  = "#f8f9fa",
    )
    return fig


def build_lift_pct_bar(sku_summary: pd.DataFrame) -> go.Figure:
    """Lift % ranked bar chart with thresholds."""
    s = sku_summary.sort_values("mean_lift_pct", ascending=False)
    colors = [
        "#2ecc71" if v >= 20 else "#3498db" if v >= 5 else "#e74c3c"
        for v in s["mean_lift_pct"]
    ]
    fig = go.Figure(go.Bar(
        x            = s["sku_id"].astype(str),
        y            = s["mean_lift_pct"],
        marker_color = colors,
        text         = s["mean_lift_pct"].round(1).astype(str) + "%",
        textposition = "outside",
    ))
    fig.add_hline(y=20, line_dash="dash", line_color="green",
                  annotation_text="High performer (20%)",
                  annotation_position="top right")
    fig.add_hline(y=5,  line_dash="dash", line_color="red",
                  annotation_text="Negligible (5%)",
                  annotation_position="bottom right")
    fig.update_layout(
        title         = "Fig 3 — Promotion Lift % per SKU  (green ≥20%  |  blue 5-20%  |  red <5%)",
        xaxis_title   = "SKU ID",
        yaxis_title   = "Mean Lift %",
        height        = 440,
        paper_bgcolor = "white",
        plot_bgcolor  = "#f8f9fa",
    )
    return fig


def build_heatmap(lift_df: pd.DataFrame, sku_summary: pd.DataFrame) -> go.Figure:
    """Lift % heatmap across SKUs and time."""
    rich_skus  = sku_summary[sku_summary["n_promo_weeks"] >= 4]["sku_id"].tolist()
    heat_data  = lift_df[lift_df["sku_id"].isin(rich_skus)]
    heat_pivot = heat_data.pivot_table(
        index="sku_id", columns="period", values="lift_pct", aggfunc="mean"
    )
    fig = go.Figure(go.Heatmap(
        z          = heat_pivot.values,
        x          = [str(c.date()) for c in heat_pivot.columns],
        y          = ["SKU " + str(r) for r in heat_pivot.index],
        colorscale = "RdYlGn",
        zmid       = 15,
        colorbar   = dict(title="Lift %"),
    ))
    fig.update_layout(
        title         = "Fig 4 — Promotion Lift % Heatmap: SKU × Week (SKUs with ≥4 promo weeks)",
        xaxis_title   = "Week",
        height        = max(350, 40 + len(rich_skus) * 22),
        paper_bgcolor = "white",
    )
    return fig


def build_sku_detail(lift_df: pd.DataFrame, sku_id: int) -> go.Figure:
    """
    Lift % and incremental sales per promoted week for a single SKU.
    Uses only columns available in promotion_output.csv:
    sku_id, period, promotion_flag, incremental_sales, lift_pct
    """
    rows = lift_df[lift_df["sku_id"] == sku_id].sort_values("period")
    if rows.empty:
        return go.Figure().update_layout(
            title=f"No promoted weeks found for SKU {sku_id}"
        )

    fig = go.Figure()

    # Lift % bars (left axis)
    fig.add_trace(go.Bar(
        x    = rows["period"],
        y    = rows["lift_pct"],
        name = "Lift %",
        marker = dict(
            color      = rows["lift_pct"],
            colorscale = "RdYlGn",
            showscale  = True,
            colorbar   = dict(title="Lift %"),
        ),
        text         = rows["lift_pct"].round(1).astype(str) + "%",
        textposition = "outside",
        yaxis        = "y",
    ))

    # Incremental sales line (right axis)
    fig.add_trace(go.Scatter(
        x    = rows["period"],
        y    = rows["incremental_sales"],
        name = "Incremental Sales",
        mode = "lines+markers",
        marker = dict(color="steelblue", size=6),
        line   = dict(color="steelblue", width=2, dash="dot"),
        yaxis  = "y2",
    ))

    fig.add_hline(y=20, line_dash="dash", line_color="green",
                  annotation_text="High performer (20%)", yref="y")
    fig.add_hline(y=5,  line_dash="dash", line_color="red",
                  annotation_text="Negligible (5%)", yref="y")

    fig.update_layout(
        title         = f"Fig 5 — SKU {sku_id}: Lift % and Incremental Sales per Promoted Week",
        xaxis_title   = "Week",
        yaxis         = dict(title="Lift %"),
        yaxis2        = dict(title="Incremental Sales (units)", overlaying="y", side="right"),
        height        = 440,
        paper_bgcolor = "white",
        plot_bgcolor  = "#f8f9fa",
        legend        = dict(orientation="h", yanchor="bottom", y=1.02),
        barmode       = "group",
    )
    return fig


# ── AI helpers ────────────────────────────────────────────────────────────────

def call_ai_narrative(ai_context: dict) -> str:
    try:
        from ai.services.module7_ai_narrative import generate_lift_narrative
        return generate_lift_narrative(context_override=ai_context)
    except Exception as e:
        return f"⚠️ AI narrative unavailable: {e}\n\n[General inference]"


def call_chart_summary(chart_id: str, chart_data: dict) -> str:
    try:
        from ai.services.module7_ai_narrative import summarise_chart
        return summarise_chart(chart_id, chart_data)
    except Exception as e:
        return f"⚠️ Summary unavailable: {e}\n\n[General inference]"


# ── Gradio Tab Builder ────────────────────────────────────────────────────────

def build_module_7_tab():
    lift_df, sku_summary, ai_context, load_error = load_outputs()

    with gr.Tab("7 · Promotion Lift Model"):

        gr.Markdown("## Module 7 — Promotion Lift Model")
        gr.Markdown(
            "Estimates causal incremental sales lift from front-page promotions "
            "using a counterfactual XGBoost model with SHAP explainability. "
            "The model predicts baseline demand *without* the promotion — "
            "lift = actual sales − counterfactual baseline."
        )

        if load_error:
            gr.Markdown(
                f"⚠️ **Outputs not found:** `{load_error}`\n\n"
                "Run the notebook at `ml/promotions/promotion_lift_model.ipynb` "
                "to generate the output files."
            )
            return

        # ── Model architecture ──
        with gr.Accordion("Model Architecture & Justification", open=False):
            gr.Markdown(f"""
| Component | Detail |
|---|---|
| **Algorithm** | XGBoost Gradient Boosted Trees |
| **Target** | `log1p(weekly_sales)` — stabilises variance across {ai_context['metrics']['total_skus']} SKUs |
| **Counterfactual** | `feat_main_page` excluded from features; model predicts no-promo baseline |
| **Ensemble** | 60% ML counterfactual + 40% matched control (±8-week window) |
| **Validation** | 5-fold TimeSeriesSplit — no future→past leakage |
| **Explainability** | SHAP TreeExplainer — exact attributions (see notebook) |
| **Uncertainty** | 90% bootstrap confidence intervals on all SKU lift estimates |
| **RAM usage** | < 50MB (lightweight CPU-friendly footprint) |
| **Features** | 16 features: price, time, lags, rolling stats, promo history, product attributes |
| **Total promo weeks analysed** | {ai_context['metrics']['total_promo_weeks']:,} |
| **Median lift across SKUs** | {ai_context['metrics']['median_lift_pct']}% |
            """)

        # ── Key findings banner ──
        kf = ai_context["key_findings"]
        gr.Markdown(
            f"> **Key findings:** "
            f"{kf['high_performers_n']} SKUs with lift >20% &nbsp;|&nbsp; "
            f"{kf['moderate_lift_n']} SKUs moderate (5-20%) &nbsp;|&nbsp; "
            f"{kf['negligible_lift_n']} SKU negligible (<5%) &nbsp;|&nbsp; "
            f"Low-evidence SKUs (< 3 promo weeks): {kf['low_evidence_skus']}"
        )

        # ── OOS Metrics ──
        gr.Markdown("### Out-of-Sample Performance Metrics")
        gr.Plot(value=build_metrics_panel(ai_context))

        with gr.Row():
            summarise_metrics_btn = gr.Button("Summarise metrics", size="sm", variant="secondary")
        metrics_summary_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        def on_summarise_metrics():
            summary = call_chart_summary("oos_metrics", ai_context["metrics"])
            return gr.update(visible=True, value=summary)

        summarise_metrics_btn.click(on_summarise_metrics, outputs=metrics_summary_box)

        # ── Incremental sales bar ──
        gr.Markdown("### Incremental Sales per SKU (with 90% Bootstrap CI)")
        gr.Plot(value=build_lift_bar(sku_summary))

        with gr.Row():
            summarise_lift_btn = gr.Button("Summarise this chart", size="sm", variant="secondary")
        lift_summary_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        def on_summarise_lift():
            data = sku_summary[
                ["sku_id", "mean_incremental_sales", "confidence_low", "confidence_high"]
            ].to_dict(orient="records")
            return gr.update(
                visible=True,
                value=call_chart_summary("incremental_sales_bar", {"data": data})
            )

        summarise_lift_btn.click(on_summarise_lift, outputs=lift_summary_box)

        # ── Lift % bar ──
        gr.Markdown("### Promotion Lift % per SKU")
        gr.Plot(value=build_lift_pct_bar(sku_summary))

        with gr.Row():
            summarise_pct_btn = gr.Button("Summarise this chart", size="sm", variant="secondary")
        pct_summary_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        def on_summarise_pct():
            data = sku_summary[
                ["sku_id", "mean_lift_pct", "n_promo_weeks"]
            ].to_dict(orient="records")
            return gr.update(
                visible=True,
                value=call_chart_summary("lift_pct_bar", {"data": data})
            )

        summarise_pct_btn.click(on_summarise_pct, outputs=pct_summary_box)

        # ── Heatmap ──
        gr.Markdown("### Lift % Heatmap — SKU × Week")
        gr.Plot(value=build_heatmap(lift_df, sku_summary))

        with gr.Row():
            summarise_heat_btn = gr.Button("Summarise this chart", size="sm", variant="secondary")
        heat_summary_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        def on_summarise_heat():
            rich = sku_summary[sku_summary["n_promo_weeks"] >= 4]
            data = rich[["sku_id", "mean_lift_pct"]].to_dict(orient="records")
            return gr.update(
                visible=True,
                value=call_chart_summary("lift_heatmap", {"data": data})
            )

        summarise_heat_btn.click(on_summarise_heat, outputs=heat_summary_box)

        # ── SKU drill-down ──
        gr.Markdown("### SKU Drill-Down — Lift % and Incremental Sales")
        sku_ids = sorted(lift_df["sku_id"].unique().tolist())

        sku_selector = gr.Dropdown(
            choices = [str(s) for s in sku_ids],
            value   = str(sku_ids[0]),
            label   = "Select SKU",
        )
        sku_plot = gr.Plot(value=build_sku_detail(lift_df, sku_ids[0]))

        with gr.Row():
            summarise_sku_btn = gr.Button("Summarise this chart", size="sm", variant="secondary")
        sku_summary_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        def on_sku_change(sku_str):
            return build_sku_detail(lift_df, int(sku_str))

        def on_summarise_sku(sku_str):
            sku_id  = int(sku_str)
            sku_row = sku_summary[sku_summary["sku_id"] == sku_id].iloc[0]
            data = {
                "sku_id"                : sku_id,
                "n_promo_weeks"         : int(sku_row["n_promo_weeks"]),
                "mean_lift_pct"         : float(sku_row["mean_lift_pct"]),
                "mean_incremental_sales": float(sku_row["mean_incremental_sales"]),
                "confidence_low"        : float(sku_row["confidence_low"]),
                "confidence_high"       : float(sku_row["confidence_high"]),
            }
            return gr.update(
                visible=True,
                value=call_chart_summary(f"sku_detail_{sku_id}", data)
            )

        sku_selector.change(on_sku_change, inputs=sku_selector, outputs=sku_plot)
        summarise_sku_btn.click(on_summarise_sku, inputs=sku_selector, outputs=sku_summary_box)

        # ── Exportable table ──
        gr.Markdown("### Exportable Model Output Table")
        gr.Markdown(
            "Full incremental sales estimates per SKU — integration contract format "
            "consumed by Module 3 (Promotion Effectiveness)."
        )
        gr.Dataframe(
            value   = sku_summary.round(2),
            headers = list(sku_summary.columns),
            label   = "SKU Lift Summary",
        )
        gr.DownloadButton(
            label = "Download promotion_output.csv",
            value = str(OUTPUTS_PATH / "promotion_output.csv"),
        )

        # ── AI Narrative ──
        gr.Markdown("---")
        gr.Markdown("### AI Model Narrative")
        gr.Markdown(
            "Generates a plain-English interpretation of the full model output. "
            "Responses are labelled `[Data-grounded]` (traceable to a specific figure) "
            "or `[General inference]` (reasoning beyond supplied data)."
        )

        generate_btn = gr.Button("Generate AI Narrative", variant="primary", size="lg")
        narrative_box = gr.Textbox(
            label       = "AI Narrative",
            lines       = 10,
            interactive = False,
            placeholder = "Click 'Generate AI Narrative' to produce the model summary...",
        )
        gr.Markdown(
            "_All figures cited in `[Data-grounded]` responses are traceable to "
            "`ml/promotions/outputs/ai_context_module7.json`. "
            "Failure cases are logged to `ai/services/failure_log.jsonl` for Module 9._"
        )

        def on_generate_narrative():
            return call_ai_narrative(ai_context)

        generate_btn.click(on_generate_narrative, outputs=narrative_box)


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    with gr.Blocks(title="Module 7 — Promotion Lift Model") as demo:
        build_module_7_tab()
    demo.launch(share=True)
