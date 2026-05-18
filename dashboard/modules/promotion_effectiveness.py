# AI-assisted: reviewed by team
"""Module 3 — Promotion Effectiveness (analytics view)."""

import gradio as gr
import plotly.graph_objects as go

from dashboard.analytics.promotions.lift_data import load_promotion_output, load_sku_lift_summary
from dashboard.components.plot_theme import COLORS, PLOTLY_LAYOUT


def _summarize(chart_id: str, data: dict) -> str:
    try:
        from ai.services.chart_summary_service import summarise_chart
        return summarise_chart(chart_id, data)
    except Exception as exc:
        return f"⚠️ Summary unavailable: {exc}\n\n[General inference]"


def build_promotion_effectiveness_tab():
    sku_summary = load_sku_lift_summary()
    lift_df = load_promotion_output()

    with gr.Tab("3 · Promotions"):
        gr.Markdown("## Module 3 — Promotion Effectiveness")
        gr.Markdown(
            "Incremental sales lift from front-page promotions (XGBoost counterfactual model). "
            "Outputs from `ml/ml_promotions_pricing/outputs/`."
        )

        if sku_summary is None:
            gr.Markdown(
                "⚠️ Promotion outputs not found. Run `ml/ml_promotions_pricing/promotion_lift_model.ipynb` first."
            )
            return

        s = sku_summary.sort_values("mean_lift_pct", ascending=False)
        fig_bar = go.Figure(go.Bar(
            x=s["sku_id"].astype(str),
            y=s["mean_incremental_sales"],
            marker_color=COLORS["teal"],
            text=s["mean_incremental_sales"].round(1),
            textposition="outside",
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Incremental sales per SKU (weekly avg)",
            xaxis_title="SKU",
            yaxis_title="Incremental units",
            height=400,
        )

        fig_pct = go.Figure(go.Bar(
            x=s["sku_id"].astype(str),
            y=s["mean_lift_pct"],
            marker_color=[
                COLORS["teal"] if v >= 20 else COLORS["blue"] if v >= 5 else COLORS["red"]
                for v in s["mean_lift_pct"]
            ],
        ))
        fig_pct.update_layout(
            **PLOTLY_LAYOUT,
            title="Promotion lift % per SKU",
            height=400,
        )

        gr.Plot(fig_bar, show_label=False)
        with gr.Row():
            btn_bar = gr.Button("Summarise this chart", size="sm")
        bar_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        gr.Plot(fig_pct, show_label=False)
        with gr.Row():
            btn_pct = gr.Button("Summarise this chart", size="sm")
        pct_box = gr.Textbox(label="AI Summary", visible=False, lines=4)

        if lift_df is not None:
            rich = sku_summary[sku_summary["n_promo_weeks"] >= 4]["sku_id"].tolist()
            heat = lift_df[lift_df["sku_id"].isin(rich)]
            pivot = heat.pivot_table(
                index="sku_id", columns="period", values="lift_pct", aggfunc="mean"
            )
            fig_heat = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[str(c.date()) if hasattr(c, "date") else str(c) for c in pivot.columns],
                y=[f"SKU {r}" for r in pivot.index],
                colorscale="RdYlGn",
                zmid=15,
            ))
            fig_heat.update_layout(**PLOTLY_LAYOUT, title="Lift % heatmap (SKU × week)", height=420)
            gr.Plot(fig_heat, show_label=False)

        high = s[s["mean_lift_pct"] >= 20]
        low = s[s["mean_lift_pct"] < 5]
        gr.Markdown(
            f"**Commentary:** {len(high)} high responders (≥20% lift), "
            f"{len(low)} negligible responders (<5%). "
            f"Prioritise promotions on high-lift SKUs; review low-lift SKUs for cost-effectiveness."
        )

        def on_bar():
            data = {
                "metrics": {
                    "top_5": s.head(5)[["sku_id", "mean_incremental_sales", "mean_lift_pct"]].to_dict("records"),
                    "median_lift_pct": float(s["mean_lift_pct"].median()),
                },
                "key_findings": [
                    f"Top SKU by lift: {int(s.iloc[0]['sku_id'])} ({s.iloc[0]['mean_lift_pct']:.1f}%)",
                ],
            }
            return gr.update(visible=True, value=_summarize("module7_lift_summary", data))

        def on_pct():
            data = {
                "metrics": {"sku_count": len(s), "avg_lift_pct": float(s["mean_lift_pct"].mean())},
                "key_findings": [f"{len(high)} SKUs exceed 20% lift threshold"],
            }
            return gr.update(visible=True, value=_summarize("module7_lift_summary", data))

        btn_bar.click(on_bar, outputs=bar_box)
        btn_pct.click(on_pct, outputs=pct_box)
