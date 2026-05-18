# AI-assisted: reviewed by team
"""Module 4 — Price Elasticity."""

import gradio as gr
import plotly.graph_objects as go

from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.analytics.pricing.elasticity_model import get_or_compute_elasticity
from dashboard.components.plot_theme import COLORS, PLOTLY_LAYOUT


def _summarize(chart_id: str, data: dict) -> str:
    try:
        from ai.services.chart_summary_service import summarise_chart
        return summarise_chart(chart_id, data)
    except Exception as exc:
        return f"⚠️ Summary unavailable: {exc}\n\n[General inference]"


def build_price_elasticity_tab():
    loader = get_data_loader()
    df = loader.get_normalized_data()
    elasticity_df = get_or_compute_elasticity(df)

    with gr.Tab("4 · Price Elasticity"):
        gr.Markdown("## Module 4 — Price Elasticity")
        gr.Markdown(
            "Log-log regression estimates price elasticity of demand per SKU "
            "(% change in demand per % change in price)."
        )

        if elasticity_df.empty:
            gr.Markdown("⚠️ Not enough data to estimate elasticity.")
            return

        s = elasticity_df.sort_values("elasticity_value")
        fig_bar = go.Figure(go.Bar(
            x=s["sku_id"].astype(str),
            y=s["elasticity_value"],
            error_y=dict(
                type="data",
                symmetric=False,
                array=(s["confidence_high"] - s["elasticity_value"]).clip(lower=0),
                arrayminus=(s["elasticity_value"] - s["confidence_low"]).clip(lower=0),
            ),
            marker_color=[
                COLORS["red"] if v < -1 else COLORS["blue"] for v in s["elasticity_value"]
            ],
        ))
        fig_bar.add_hline(y=-1, line_dash="dash", line_color=COLORS["amber"],
                          annotation_text="Unit elastic (-1)")
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Elasticity coefficient by SKU (most elastic → least)",
            xaxis_title="SKU",
            yaxis_title="Elasticity",
            height=420,
        )
        gr.Plot(fig_bar, show_label=False)

        sku_choices = [str(x) for x in sorted(elasticity_df["sku_id"].unique())]
        sku_sel = gr.Dropdown(choices=sku_choices, value=sku_choices[0], label="SKU demand curve")
        curve_plot = gr.Plot()

        def demand_curve(sku_str):
            sku_id = int(sku_str)
            sub = df[df["sku_id"] == sku_id].sort_values("period")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sub["price"], y=sub["demand_units"],
                mode="markers", name="Observed",
                marker=dict(color=COLORS["teal"], size=5, opacity=0.6),
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title=f"SKU {sku_id}: price vs demand",
                xaxis_title="Price",
                yaxis_title="Demand (units)",
                height=360,
            )
            return fig

        curve_plot.value = demand_curve(sku_choices[0])
        sku_sel.change(demand_curve, sku_sel, curve_plot)

        with gr.Row():
            btn = gr.Button("Summarise elasticity chart", size="sm")
        summary_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        def on_summarize():
            data = {
                "metrics": elasticity_df[
                    ["sku_id", "elasticity_value", "confidence_low", "confidence_high"]
                ].head(10).to_dict("records"),
                "key_findings": [
                    f"{len(elasticity_df[elasticity_df['elasticity_value'] < -1])} elastic SKUs",
                ],
            }
            return gr.update(visible=True, value=_summarize("module4_elasticity", data))

        btn.click(on_summarize, outputs=summary_box)
