# Module 4 — Price Elasticity
# Owner: Analytics / ML Pod B
# Description: Visualises the ElasticityOutput contract — own-price
#              elasticity per SKU (log-log OLS) with confidence intervals,
#              plus a constant-elasticity demand curve. Pure consumer:
#              the regression is fit offline in ml/pricing/.

import gradio as gr
import numpy as np
import plotly.graph_objects as go

from dashboard.analytics.common.elasticity_loader import get_elasticity_loader
from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.components import ui
from ai.services import narrative_service

_ELASTIC = "#4d9bff"     # |e|>1  price-sensitive
_INELASTIC = "#f59e0b"   # |e|<1  pricing power


def _elasticity_bar(cls_df) -> go.Figure:
    fig = go.Figure()
    d = cls_df.dropna(subset=["elasticity_value"]).sort_values("elasticity_value")
    if d.empty:
        fig.update_layout(**ui.plotly_layout(400))
        return fig
    colors = [_ELASTIC if v < -1 else _INELASTIC for v in d["elasticity_value"]]
    fig.add_trace(go.Bar(
        x=d["sku_id"].astype(str), y=d["elasticity_value"],
        marker_color=colors,
        error_y=dict(
            type="data", symmetric=False,
            array=(d["confidence_high"] - d["elasticity_value"]).clip(lower=0),
            arrayminus=(d["elasticity_value"] - d["confidence_low"]).clip(lower=0),
            color="rgba(128,140,165,0.45)", thickness=1,
        ),
        hovertemplate="SKU %{x}<br>Elasticity %{y:.2f}<extra></extra>",
    ))
    fig.add_hline(y=-1, line_dash="dot", line_color="rgba(128,140,165,0.6)",
                  annotation_text="unit-elastic (−1)",
                  annotation_font_color="#8a9bb5")
    fig.update_layout(**ui.plotly_layout(
        400, xaxis_title="SKU", yaxis_title="Own-price elasticity (β)"))
    return fig


def _demand_curve(sku_id: int, elasticity: float) -> go.Figure:
    """Constant-elasticity curve anchored at the SKU's observed centroid,
    overlaid on the observed price/demand scatter."""
    fig = go.Figure()
    if elasticity is None:
        fig.update_layout(**ui.plotly_layout(330))
        return fig
    df = get_data_loader().get_normalized_data()
    g = df[(df["sku_id"] == int(sku_id)) & (df["demand_units"] > 0)]
    if g.empty:
        fig.update_layout(**ui.plotly_layout(330))
        return fig

    p_bar, d_bar = float(g["price"].mean()), float(g["demand_units"].mean())
    px = np.linspace(g["price"].min() * 0.85, g["price"].max() * 1.15, 60)
    dy = d_bar * (px / p_bar) ** elasticity

    fig.add_trace(go.Scatter(
        x=g["price"], y=g["demand_units"], mode="markers", name="Observed weeks",
        marker=dict(size=6, color="rgba(128,140,165,0.55)"),
        hovertemplate="Price %{x:.2f}<br>Demand %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=px, y=dy, mode="lines", name=f"Fitted (β={elasticity:.2f})",
        line=dict(color=_ELASTIC, width=2.5),
        hovertemplate="Price %{x:.2f}<br>Modelled %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        330, xaxis_title="Price", yaxis_title="Weekly demand (units)"))
    return fig


def build_price_elasticity_tab():
    """Render Module 4 inside a running gr.Blocks context."""
    with gr.Tab("4. Price Elasticity"):
        loader = get_elasticity_loader()
        if not loader.available():
            gr.HTML(ui.warn(
                "⚠️ No elasticity output found.<br>Run "
                "<code>python ml/pricing/price_elasticity_model.py</code> to "
                "generate <code>ml/pricing/elasticity_output.csv</code>."))
            return

        cls = loader.classify()
        m = loader.headline_metrics()
        skus = loader.get_sku_list()

        gr.HTML(ui.header(
            "Price Elasticity — Module 4",
            "Own-price elasticity per SKU from a log–log OLS regression "
            "(promotion-controlled). β &lt; −1 = elastic (price-sensitive); "
            "−1 &lt; β &lt; 0 = inelastic (pricing power). Whiskers are 95% CIs."))

        gr.HTML(ui.kpi_cards([
            ("SKUs fitted", f"{m.get('num_fitted', 0)}/{m.get('num_skus', 0)}",
             "valid regressions"),
            ("Median β", f"{m.get('median_elasticity', float('nan')):.2f}",
             "typical SKU"),
            ("Elastic", f"{m.get('num_elastic', 0)}", "β < −1"),
            ("Inelastic", f"{m.get('num_inelastic', 0)}", "−1 < β < 0"),
            ("Low evidence", f"{m.get('num_low_evidence', 0)}", "weak fit (R²<.05)"),
        ]))

        gr.Markdown("#### Own-price elasticity by SKU")
        gr.Plot(value=_elasticity_bar(cls), show_label=False, container=False)

        with gr.Row():
            with gr.Column(scale=3):
                sku_dd = gr.Dropdown(skus, value=skus[0],
                                     label="SKU — demand curve")
                curve = gr.Plot(
                    value=_demand_curve(skus[0], loader.get_elasticity(skus[0])),
                    show_label=False, container=False)
            with gr.Column(scale=2):
                gr.Markdown("#### AI summary (8b)")
                sum_btn = gr.Button("📝 Summarise price elasticity",
                                    variant="primary")
                sum_out = gr.Markdown()

        with gr.Accordion("Per-SKU elasticity table", open=False):
            gr.Dataframe(
                value=cls[["sku_id", "elasticity_value", "confidence_low",
                           "confidence_high", "class", "r_squared", "n_obs"]],
                interactive=False, wrap=True)

        sku_dd.change(
            lambda s: _demand_curve(s, loader.get_elasticity(s)),
            sku_dd, curve)
        sum_btn.click(
            lambda: narrative_service.summarise_scope("price_elasticity"),
            None, sum_out)


if __name__ == "__main__":
    with gr.Blocks(title="Price Elasticity") as demo:
        build_price_elasticity_tab()
    demo.launch()
