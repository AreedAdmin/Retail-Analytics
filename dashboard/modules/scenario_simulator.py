# Module 5 — Scenario Simulator
# Owner: Analytics + Dashboard
# Description: What-if pricing. Combines Module 4 elasticity with a
#              baseline (mean weekly demand/price) to project the demand
#              and revenue impact of a price change. No new model — pure
#              constant-elasticity arithmetic on existing outputs.

import gradio as gr
import plotly.graph_objects as go

from dashboard.analytics.common.elasticity_loader import get_elasticity_loader
from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.analytics.pricing import project_price_change
from dashboard.components import ui
from ai.services import narrative_service


def _baseline(sku_id: int):
    """Mean weekly demand & price for the SKU (the scenario anchor)."""
    df = get_data_loader().get_normalized_data()
    g = df[(df["sku_id"] == int(sku_id)) & (df["demand_units"] > 0)]
    if g.empty:
        return None
    return float(g["demand_units"].mean()), float(g["price"].mean())


def _project(sku_id: int, pct: float):
    el = get_elasticity_loader().get_elasticity(sku_id)
    base = _baseline(sku_id)
    if el is None or base is None:
        return None, el
    d0, p0 = base
    return project_price_change(el, d0, p0, pct), el


def _waterfall(r: dict) -> go.Figure:
    fig = go.Figure()
    if not r:
        fig.update_layout(**ui.plotly_layout(330))
        return fig
    base_rev = r["baseline_revenue"]
    price_effect = base_rev * (r["price_change_pct"] / 100.0)
    volume_effect = r["new_revenue"] - (base_rev + price_effect)
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Baseline", "Price effect", "Volume effect", "Projected"],
        y=[base_rev, price_effect, volume_effect, r["new_revenue"]],
        connector=dict(line=dict(color="rgba(128,140,165,0.4)")),
        increasing=dict(marker=dict(color="#4d9bff")),
        decreasing=dict(marker=dict(color="#ef4444")),
        totals=dict(marker=dict(color="#f59e0b")),
        hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        330, yaxis_title="Weekly revenue", showlegend=False))
    return fig


def _cards(r: dict, el: float) -> str:
    if not r:
        return ui.warn("No elasticity available for this SKU — cannot "
                       "simulate. Pick another SKU.")
    sign = "▲" if r["revenue_change_pct"] >= 0 else "▼"
    return ui.kpi_cards([
        ("Elasticity β", f"{el:.2f}",
         "elastic" if el < -1 else "inelastic"),
        ("Price", f"{r['baseline_price']:.2f} → {r['new_price']:.2f}",
         f"{r['price_change_pct']:+.0f}%"),
        ("Weekly demand", f"{r['baseline_demand']:,.0f} → {r['new_demand']:,.0f}",
         f"{r['demand_change_pct']:+.1f}%"),
        ("Weekly revenue",
         f"{r['baseline_revenue']:,.0f} → {r['new_revenue']:,.0f}",
         f"{sign} {r['revenue_change_pct']:+.1f}%"),
    ])


def build_scenario_simulator_tab():
    """Render Module 5 inside a running gr.Blocks context."""
    with gr.Tab("5. Scenario Simulator"):
        eloader = get_elasticity_loader()
        if not eloader.available():
            gr.HTML(ui.warn(
                "⚠️ Scenario simulation needs the elasticity model.<br>Run "
                "<code>python ml/pricing/price_elasticity_model.py</code> "
                "first (Module 4)."))
            return

        skus = eloader.get_sku_list()
        gr.HTML(ui.header(
            "Scenario Simulator — Module 5",
            "What-if pricing. Projects demand &amp; revenue for a price move "
            "using each SKU's estimated elasticity against its mean weekly "
            "baseline: demand%% ≈ β·price%%; revenue compounds both."))

        with gr.Row():
            sku_dd = gr.Dropdown(skus, value=skus[0], label="SKU", scale=2)
            slider = gr.Slider(-30, 30, value=10, step=1,
                               label="Price change (%)", scale=3)

        r0, el0 = _project(skus[0], 10)
        cards = gr.HTML(value=_cards(r0, el0))
        with gr.Row():
            with gr.Column(scale=3):
                wf = gr.Plot(value=_waterfall(r0), show_label=False,
                             container=False)
            with gr.Column(scale=2):
                gr.Markdown("#### AI strategic memo (8b)")
                memo_btn = gr.Button("🧠 Generate pricing memo",
                                     variant="primary")
                memo = gr.Markdown()

        def _update(sku, pct):
            r, el = _project(sku, pct)
            return _cards(r, el), _waterfall(r)

        def _memo(sku, pct):
            r, el = _project(sku, pct)
            if not r:
                return "No elasticity for this SKU.\n\n[Data-grounded]"
            ctx = {
                "module_name": "scenario_simulator",
                "chart_id": "what_if_pricing",
                "metrics": {"sku_id": int(sku), "elasticity": el, **r},
                "key_findings": [
                    f"SKU {int(sku)} elasticity {el:.2f} "
                    f"({'elastic' if el < -1 else 'inelastic'}).",
                    f"A {r['price_change_pct']:+.0f}% price move → "
                    f"{r['demand_change_pct']:+.1f}% demand, "
                    f"{r['revenue_change_pct']:+.1f}% revenue.",
                ],
            }
            return narrative_service.summarise_payload(ctx)

        sku_dd.change(_update, [sku_dd, slider], [cards, wf])
        slider.change(_update, [sku_dd, slider], [cards, wf])
        memo_btn.click(_memo, [sku_dd, slider], memo)


if __name__ == "__main__":
    with gr.Blocks(title="Scenario Simulator") as demo:
        build_scenario_simulator_tab()
    demo.launch()
