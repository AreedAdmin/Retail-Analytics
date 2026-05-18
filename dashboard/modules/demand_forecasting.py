# AI-assisted: reviewed by [name]
# Module 6 — Demand Forecasting
# Owner: ML Pod
# Description: Visualises the Forecast contract (actual vs predicted + CI band)
#              and model quality metrics. Pure consumer of
#              ml/ml_forecasting/outputs/ — does NOT run the model.

import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from dashboard.analytics.common.forecast_loader import get_forecast_loader

# ─────────────────────────────────────────────────────────────
# COLOURS  (kept identical to modules/overview.py)
# ─────────────────────────────────────────────────────────────
C = {
    "bg": "#0d1b2a", "panel": "#112236", "border": "#1e3a55",
    "teal": "#00d4aa", "amber": "#f59e0b", "purple": "#7c5cbf",
    "blue": "#3b82f6", "text": "#e8edf5", "muted": "#5a7a9a",
    "grid": "rgba(30,58,85,0.5)",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=C["panel"], plot_bgcolor=C["panel"],
    font=dict(color=C["muted"], size=11),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(gridcolor=C["grid"], linecolor=C["border"], tickfont=dict(size=10)),
    yaxis=dict(gridcolor=C["grid"], linecolor=C["border"], tickfont=dict(size=10)),
)

GRADIO_CSS = """
body, .gradio-container, .main, .wrap, .gap { background:#0d1b2a !important; color:#e8edf5 !important; }
.block, .form, .panel { background:#112236 !important; border:1px solid #1e3a55 !important; border-radius:12px !important; }
.plotly-graph-div { background:#112236 !important; }
footer { display:none !important; }
"""

KPI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');
.fc-row{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:4px 0 12px}
.fc-card{background:#112236;border:1px solid #1e3a55;border-radius:12px;padding:16px 14px;border-top:3px solid #00d4aa}
.fc-card.amber{border-top-color:#f59e0b}.fc-card.blue{border-top-color:#3b82f6}.fc-card.purple{border-top-color:#7c5cbf}
.fc-lbl{font:600 10px/1 'DM Sans',sans-serif;text-transform:uppercase;letter-spacing:.1em;color:#ffffff;margin-bottom:8px}
.fc-val{font:700 28px/1 'Space Grotesk',sans-serif;color:#fff}
.fc-sub{font-size:11px;color:#8a9bb5;margin-top:6px}
.fc-title{font:600 20px/1.2 'Space Grotesk',sans-serif;color:#fff;margin-bottom:4px}
.fc-note{font-size:12px;color:#8a9bb5}
.fc-warn{background:#1a2d42;border:1px solid #2a4a6a;border-radius:12px;padding:24px;color:#e8edf5;font-size:13px}
</style>
"""


# ─────────────────────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────────────────────

def make_forecast_chart(sku_df: pd.DataFrame) -> go.Figure:
    """Actual vs predicted with the 95% interval band for one SKU."""
    fig = go.Figure()
    if sku_df.empty:
        fig.update_layout(**PLOTLY_LAYOUT, height=360)
        return fig

    x = sku_df["period"]
    # CI band (upper then lower, fill between)
    fig.add_trace(go.Scatter(
        x=x, y=sku_df["y_upper"], mode="lines",
        line=dict(width=0), hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=x, y=sku_df["y_lower"], mode="lines", name="95% interval",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(0,212,170,0.13)",
        hovertemplate="Lower %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=sku_df["y_pred"], mode="lines", name="Forecast",
        line=dict(color=C["teal"], width=2.5),
        hovertemplate="%{x|%Y-%m-%d}<br>Forecast: %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=sku_df["y_true"], mode="lines+markers", name="Actual",
        line=dict(color=C["amber"], width=2, dash="dot"),
        marker=dict(size=5),
        hovertemplate="%{x|%Y-%m-%d}<br>Actual: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=360, hovermode="x unified",
        legend=dict(orientation="h", y=-0.18, x=0,
                    font=dict(size=11, color=C["muted"]),
                    bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# HTML FRAGMENTS
# ─────────────────────────────────────────────────────────────

def _kpi_header_html(summary: dict) -> str:
    if not summary:
        return KPI_CSS + '<div class="fc-warn">Model summary not available.</div>'
    g = lambda k, d=0: summary.get(k, d)
    return KPI_CSS + f"""
    <div class="fc-title">Demand Forecasting — Model 6</div>
    <div class="fc-note">Backtest of <b>{g('model_name','?')}</b> on the held-out
      test weeks. Errors in real sales units; coverage = % of actuals inside the
      interval.</div>
    <div class="fc-row">
      <div class="fc-card"><div class="fc-lbl">Model</div>
        <div class="fc-val" style="font-size:18px">{g('model_name','?')}</div>
        <div class="fc-sub">selected on validation</div></div>
      <div class="fc-card amber"><div class="fc-lbl">Test MAE</div>
        <div class="fc-val">{float(g('MAE')):,.1f}</div>
        <div class="fc-sub">mean abs error</div></div>
      <div class="fc-card blue"><div class="fc-lbl">Test RMSE</div>
        <div class="fc-val">{float(g('RMSE')):,.1f}</div>
        <div class="fc-sub">penalises spikes</div></div>
      <div class="fc-card purple"><div class="fc-lbl">Test MAPE</div>
        <div class="fc-val">{float(g('MAPE')):,.1f}%</div>
        <div class="fc-sub">pct error</div></div>
      <div class="fc-card"><div class="fc-lbl">95% Coverage</div>
        <div class="fc-val">{float(g('cov95')):,.1f}%</div>
        <div class="fc-sub">target ~95</div></div>
    </div>"""


def _worst_skus_html(per_sku: pd.DataFrame, n: int = 8) -> str:
    if per_sku.empty:
        return ""
    rows = (per_sku.sort_values("MAE", ascending=False)
            .head(n)[["sku", "MAE", "RMSE", "MAPE"]])
    body = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:7px 12px;'
        f'border-bottom:1px solid #1e3a55;font-size:11px;color:#e8edf5">'
        f'<span style="color:#fff;font-weight:600">SKU {int(r.sku)}</span>'
        f'<span>MAE {r.MAE:,.0f}</span><span>RMSE {r.RMSE:,.0f}</span>'
        f'<span style="color:#f59e0b">MAPE {r.MAPE:,.0f}%</span></div>'
        for r in rows.itertuples(index=False)
    )
    return (
        '<div class="panel-wrap"><div class="fc-lbl" style="padding:10px 12px;'
        'color:#ef4444">Worst SKUs by MAE (test)</div>'
        f'<div style="background:#0a1520">{body}</div></div>'
    )


# ─────────────────────────────────────────────────────────────
# TAB
# ─────────────────────────────────────────────────────────────

def build_demand_forecasting_tab():
    """Render Module 6 inside a running gr.Blocks context."""
    loader = get_forecast_loader()

    with gr.Tab("6. Demand Forecasting"):
        if not loader.available():
            gr.HTML(
                KPI_CSS + '<div class="fc-warn">⚠️ No forecast output found.<br>'
                'Run <code>ml/ml_forecasting/forecasting.ipynb</code> top-to-bottom '
                'to generate <code>ml/ml_forecasting/outputs/forecast.csv</code>, '
                'then reload this page.</div>'
            )
            return

        summary = loader.load_summary()
        per_sku = loader.load_per_sku_metrics()
        skus = loader.get_sku_list()

        gr.HTML(value=_kpi_header_html(summary))

        with gr.Row():
            with gr.Column(scale=3):
                sku_dd = gr.Dropdown(
                    choices=skus, value=skus[0], label="SKU",
                    interactive=True,
                )
                plot = gr.Plot(
                    value=make_forecast_chart(loader.get_sku_forecast(skus[0])),
                    show_label=False, container=False,
                )
            with gr.Column(scale=1):
                gr.HTML(value=_worst_skus_html(per_sku))

        def _update(sku_id):
            return make_forecast_chart(loader.get_sku_forecast(sku_id))

        sku_dd.change(_update, inputs=sku_dd, outputs=plot)


# ─────────────────────────────────────────────────────────────
# STANDALONE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with gr.Blocks(title="Demand Forecasting — Retail Dashboard") as demo:
        build_demand_forecasting_tab()
    demo.launch(
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
        ),
        css=GRADIO_CSS,
    )
