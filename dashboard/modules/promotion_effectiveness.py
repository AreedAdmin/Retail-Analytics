# Module 3 — Promotion Effectiveness
# Owner: Analytics / ML Pod B
# Description: Visualises the PromotionOutput contract — which SKUs respond
#              to promotions and by how much. Click-to-summarise routes the
#              grounded context through the AI layer (Module 8b).

import gradio as gr
import plotly.graph_objects as go

from dashboard.analytics.common.promotion_loader import get_promotion_loader
from dashboard.components import ui
from ai.services import narrative_service


def _lift_bar(summary) -> go.Figure:
    """Mean lift % by SKU, sorted, with confidence whiskers."""
    fig = go.Figure()
    if summary.empty:
        fig.update_layout(**ui.plotly_layout(380))
        return fig
    s = summary.sort_values("mean_lift_pct", ascending=False)
    fig.add_trace(go.Bar(
        x=s["sku_id"].astype(str), y=s["mean_lift_pct"],
        marker_color=ui.ACCENT,
        error_y=dict(
            type="data", symmetric=False,
            array=(s["confidence_high"] - s["mean_lift_pct"]).clip(lower=0),
            arrayminus=(s["mean_lift_pct"] - s["confidence_low"]).clip(lower=0),
            color="rgba(128,140,165,0.5)", thickness=1,
        ),
        hovertemplate="SKU %{x}<br>Mean lift %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        380, xaxis_title="SKU", yaxis_title="Mean lift %"))
    return fig


def _sku_timeline(df) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        fig.update_layout(**ui.plotly_layout(320))
        return fig
    fig.add_trace(go.Scatter(
        x=df["period"], y=df["lift_pct"], mode="lines+markers",
        line=dict(color=ui.ACCENT, width=2), marker=dict(size=5),
        name="Lift %",
        hovertemplate="%{x|%Y-%m-%d}<br>Lift %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        320, yaxis_title="Lift %", hovermode="x unified"))
    return fig


def build_promotion_effectiveness_tab():
    """Render Module 3 inside a running gr.Blocks context."""
    with gr.Tab("3. Promotion Effectiveness"):
        loader = get_promotion_loader()
        if not loader.available():
            gr.HTML(ui.warn(
                "⚠️ No promotion output found.<br>Run "
                "<code>ml/promotions/promotion_lift_model.ipynb</code> to "
                "generate <code>ml/promotions/promotion_output.csv</code>."))
            return

        summary = loader.load_summary()
        m = loader.headline_metrics()
        skus = loader.get_sku_list()

        gr.HTML(ui.header(
            "Promotion Effectiveness — Module 3",
            "Incremental sales and % lift attributed to promotions per SKU. "
            "Whiskers show the per-SKU confidence interval."))

        gr.HTML(ui.kpi_cards([
            ("SKUs analysed", f"{m.get('num_skus', 0):,}", "with promo weeks"),
            ("Median lift", f"{m.get('median_lift_pct', 0):.1f}%", "typical SKU"),
            ("Max lift", f"{m.get('max_lift_pct', 0):.1f}%", "best responder"),
            ("Incremental units", f"{m.get('total_incremental_sales', 0):,.0f}",
             "promo-attributed"),
            ("Promo weeks", f"{m.get('total_promo_weeks', 0):,}", "total"),
        ]))

        gr.Markdown("#### Mean promotional lift by SKU")
        gr.Plot(value=_lift_bar(summary), show_label=False, container=False)

        with gr.Row():
            with gr.Column(scale=3):
                sku_dd = gr.Dropdown(skus, value=skus[0], label="SKU detail")
                ts_plot = gr.Plot(value=_sku_timeline(loader.get_sku_output(skus[0])),
                                   show_label=False, container=False)
            with gr.Column(scale=2):
                gr.Markdown("#### AI summary (8b)")
                sum_btn = gr.Button("📝 Summarise promotion effectiveness",
                                    variant="primary")
                sum_out = gr.Markdown()

        sku_dd.change(lambda s: _sku_timeline(loader.get_sku_output(s)),
                      sku_dd, ts_plot)
        sum_btn.click(lambda: narrative_service.summarise_scope("promotion_lift"),
                      None, sum_out)


if __name__ == "__main__":
    with gr.Blocks(title="Promotion Effectiveness") as demo:
        build_promotion_effectiveness_tab()
    demo.launch()
