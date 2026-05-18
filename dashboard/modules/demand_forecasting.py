# AI-assisted: reviewed by team
"""Module 6 — Demand Forecasting."""

import gradio as gr
import plotly.graph_objects as go

from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.analytics.forecasting.simple_forecast import HORIZON, write_forecast_outputs
from dashboard.components.plot_theme import COLORS, PLOTLY_LAYOUT


def _summarize(chart_id: str, data: dict) -> str:
    try:
        from ai.services.chart_summary_service import summarise_chart
        return summarise_chart(chart_id, data)
    except Exception as exc:
        return f"⚠️ Summary unavailable: {exc}\n\n[General inference]"


def build_demand_forecasting_tab():
    loader = get_data_loader()
    df = loader.get_normalized_data()
    forecast_df = write_forecast_outputs(df)

    with gr.Tab("6 · Forecasting"):
        gr.Markdown("## Module 6 — Demand Forecasting")
        gr.Markdown(
            f"Per-SKU demand forecast for the next **{HORIZON}** weeks "
            "(linear trend baseline; replace with ML notebook outputs when available)."
        )

        if forecast_df.empty:
            gr.Markdown("⚠️ Could not generate forecasts.")
            return

        sku_choices = [str(s) for s in sorted(forecast_df["sku_id"].unique())]
        sku_sel = gr.Dropdown(sku_choices, value=sku_choices[0], label="Select SKU")
        forecast_plot = gr.Plot()
        metrics_md = gr.Markdown()

        def render(sku_str):
            sku_id = int(sku_str)
            hist = df[df["sku_id"] == sku_id].sort_values("period")
            fc = forecast_df[forecast_df["sku_id"] == sku_id]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist["period"], y=hist["demand_units"],
                name="Historical", mode="lines",
                line=dict(color=COLORS["blue"], width=2),
            ))
            fig.add_trace(go.Scatter(
                x=fc["period"], y=fc["y_pred"],
                name="Forecast", mode="lines+markers",
                line=dict(color=COLORS["teal"], width=2, dash="dash"),
            ))
            fig.add_trace(go.Scatter(
                x=list(fc["period"]) + list(fc["period"][::-1]),
                y=list(fc["y_upper"]) + list(fc["y_lower"][::-1]),
                fill="toself", fillcolor="rgba(0,212,170,0.12)",
                line=dict(width=0), name="80% interval", showlegend=True,
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title=f"SKU {sku_id} — demand forecast",
                xaxis_title="Period",
                yaxis_title="Units",
                height=400,
            )
            recent = hist.tail(8)["demand_units"].mean()
            prior = hist.iloc[-16:-8]["demand_units"].mean() if len(hist) >= 16 else recent
            trend = "flat"
            if prior > 0:
                chg = (recent - prior) / prior
                trend = "up" if chg > 0.05 else "down" if chg < -0.05 else "flat"
            md = (
                f"**Trend:** {trend} · **Model:** linear_trend_baseline · "
                f"**Next-period forecast:** {fc['y_pred'].iloc[0]:.0f} units "
                f"({fc['y_lower'].iloc[0]:.0f}–{fc['y_upper'].iloc[0]:.0f} interval)"
            )
            return fig, md

        init = render(sku_choices[0])
        forecast_plot.value = init[0]
        metrics_md.value = init[1]
        sku_sel.change(render, sku_sel, [forecast_plot, metrics_md])

        with gr.Row():
            narr_btn = gr.Button("Generate AI narrative", variant="primary")
        narr_box = gr.Textbox(label="AI narrative", lines=6, interactive=False)

        def on_narrative():
            data = {
                "metrics": {"horizon": HORIZON, "num_skus": int(forecast_df["sku_id"].nunique())},
                "key_findings": ["Forecasts use linear trend on last 52 weeks per SKU"],
            }
            return _summarize("module6_forecast", data)

        narr_btn.click(on_narrative, outputs=narr_box)
