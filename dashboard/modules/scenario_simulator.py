# AI-assisted: reviewed by team
"""Module 5 — Scenario Simulator."""

import gradio as gr
import plotly.graph_objects as go

from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.analytics.pricing.elasticity_model import get_or_compute_elasticity
from dashboard.analytics.scenarios.scenario_engine import (
    DEFAULT_SCENARIOS,
    aggregate_scenario,
    run_scenarios,
    write_scenario_context,
)
from dashboard.components.plot_theme import COLORS, PLOTLY_LAYOUT


def _memo(price_pct: float, agg: dict, sku_id: str) -> str:
    if not agg:
        return "[General inference] Insufficient data for this scenario."
    d = agg["weighted_demand_change_pct"]
    r = agg["weighted_revenue_change_pct"]
    beneficial = r > 0
    scope = f"SKU {sku_id}" if sku_id != "All" else "portfolio (all SKUs)"
    lines = [
        f"## Strategic memo — {price_pct:+.0f}% price change ({scope})",
        "",
        f"**[Data-grounded]** Projected demand change: **{d:+.1f}%**",
        f"**[Data-grounded]** Projected revenue change: **{r:+.1f}%**",
        "",
        f"**Recommendation:** {'Proceed' if beneficial else 'Avoid'} this price change — "
        f"revenue is expected to {'increase' if beneficial else 'decrease'} based on elasticity estimates.",
        "",
        "**Caveats:** [General inference] Assumes constant elasticity, no competitive "
        "reaction, and stable promotion mix. External shocks are not modelled.",
    ]
    return "\n".join(lines)


def build_scenario_simulator_tab():
    loader = get_data_loader()
    df = loader.get_normalized_data()
    elasticity_df = get_or_compute_elasticity(df)
    scenario_df = run_scenarios(elasticity_df, df)
    write_scenario_context(scenario_df)

    with gr.Tab("5 · Scenarios"):
        gr.Markdown("## Module 5 — Scenario Simulator")
        gr.Markdown("What-if pricing scenarios using estimated elasticity.")

        if scenario_df.empty:
            gr.Markdown("⚠️ Run elasticity estimation first (Module 4).")
            return

        sku_choices = ["All"] + [str(s) for s in sorted(scenario_df["sku_id"].unique())]
        scenario_choices = [f"{p:+.0f}%" for p in DEFAULT_SCENARIOS]

        with gr.Row():
            sku_sel = gr.Dropdown(sku_choices, value="All", label="SKU")
            scenario_sel = gr.Dropdown(scenario_choices, value="+10%", label="Price change")

        memo_box = gr.Markdown()
        chart_plot = gr.Plot()

        def build_charts(sku, scenario_label):
            pct = float(scenario_label.replace("%", ""))
            if sku == "All":
                sub = scenario_df[scenario_df["price_change_pct"] == pct]
                agg_d = sub.groupby("sku_id")["demand_change_pct"].mean()
                agg_r = sub.groupby("sku_id")["revenue_change_pct"].mean()
                agg = aggregate_scenario(scenario_df, pct)
            else:
                sid = int(sku)
                sub = scenario_df[
                    (scenario_df["sku_id"] == sid) & (scenario_df["price_change_pct"] == pct)
                ]
                agg = sub.iloc[0].to_dict() if not sub.empty else {}
                agg_d = sub.set_index("sku_id")["demand_change_pct"]
                agg_r = sub.set_index("sku_id")["revenue_change_pct"]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Demand Δ%", x=["Demand"], y=[agg.get("demand_change_pct", agg.get("weighted_demand_change_pct", 0))],
                marker_color=COLORS["blue"],
            ))
            fig.add_trace(go.Bar(
                name="Revenue Δ%", x=["Revenue"], y=[agg.get("revenue_change_pct", agg.get("weighted_revenue_change_pct", 0))],
                marker_color=COLORS["teal"],
            ))
            fig.update_layout(**PLOTLY_LAYOUT, title=f"Scenario: {pct:+.0f}% price", barmode="group", height=320)
            memo = _memo(pct, agg if sku == "All" else {
                "weighted_demand_change_pct": float(sub["demand_change_pct"].iloc[0]) if not sub.empty else 0,
                "weighted_revenue_change_pct": float(sub["revenue_change_pct"].iloc[0]) if not sub.empty else 0,
            }, sku)
            return memo, fig

        init = build_charts("All", "+10%")
        memo_box.value = init[0]
        chart_plot.value = init[1]

        def on_change(sku, scen):
            return build_charts(sku, scen)

        sku_sel.change(on_change, [sku_sel, scenario_sel], [memo_box, chart_plot])
        scenario_sel.change(on_change, [sku_sel, scenario_sel], [memo_box, chart_plot])

        export_btn = gr.Button("Copy memo to export buffer", size="sm")
        export_out = gr.Textbox(label="Memo (copy for external use)", lines=8)

        def export_memo(sku, scen):
            memo, _ = build_charts(sku, scen)
            return memo

        export_btn.click(export_memo, [sku_sel, scenario_sel], export_out)

        # Portfolio waterfall across scenarios
        portfolio = [aggregate_scenario(scenario_df, p) for p in DEFAULT_SCENARIOS]
        portfolio = [p for p in portfolio if p]
        fig_w = go.Figure(go.Waterfall(
            x=[f"{p['price_change_pct']:+.0f}%" for p in portfolio],
            y=[p["weighted_revenue_change_pct"] for p in portfolio],
            measure=["relative"] * len(portfolio),
        ))
        fig_w.update_layout(**PLOTLY_LAYOUT, title="Portfolio revenue impact by scenario", height=360)
        gr.Plot(fig_w, show_label=False)
