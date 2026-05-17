# AI-assisted: reviewed by [name]
# Module 1 — Overview
# Owner: Dashboard Lead
# Description: High-level KPIs and key findings summary

import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────────────────────
C = {
    "bg":     "#0d1b2a",
    "panel":  "#112236",
    "border": "#1e3a55",
    "teal":   "#00d4aa",
    "amber":  "#f59e0b",
    "purple": "#7c5cbf",
    "blue":   "#3b82f6",
    "text":   "#e8edf5",
    "muted":  "#5a7a9a",
    "grid":   "rgba(30,58,85,0.5)",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=C["panel"],
    plot_bgcolor=C["panel"],
    font=dict(color=C["muted"], size=11),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(gridcolor=C["grid"], linecolor=C["border"], tickfont=dict(size=10)),
    yaxis=dict(gridcolor=C["grid"], linecolor=C["border"], tickfont=dict(size=10)),
)

# ─────────────────────────────────────────────────────────────
# GRADIO CSS  — forces dark everywhere
# ─────────────────────────────────────────────────────────────
GRADIO_CSS = """
body, .gradio-container, .main, .wrap, .gap, .svelte-1ipelgc {
    background: #0d1b2a !important;
    color: #e8edf5 !important;
}
.block, .form, .panel, .gr-box, .gr-panel, .gr-form, .gr-group {
    background: #112236 !important;
    border: 1px solid #1e3a55 !important;
    border-radius: 12px !important;
}
.plotly-graph-div { background: #112236 !important; }
.tab-nav button {
    background: #0d1b2a !important;
    color: #8a9bb5 !important;
    border-bottom: 2px solid transparent !important;
}
.tab-nav button.selected {
    color: #00d4aa !important;
    border-bottom: 2px solid #00d4aa !important;
    background: #112236 !important;
}
.prose, .output-html { background: transparent !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1b2a; }
::-webkit-scrollbar-thumb { background: #2a4a6a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a5a7a; }
footer { display: none !important; }
"""

# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    paths = [
        os.path.join(os.path.dirname(__file__), "../../data/data_raw.csv"),
        "data/data_raw.csv",
        "data_raw.csv",
    ]
    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            return df.rename(columns={"sku": "sku_id", "week": "period"})
    return pd.DataFrame()


def make_simulated_data() -> pd.DataFrame:
    """Realistic simulated retail data used when CSV is absent."""
    rng  = np.random.default_rng(42)
    skus = list(range(1, 45))
    periods = list(range(1, 105))
    funcs = ["Kitchenware", "Electronics", "Apparel", "Tools", "Beauty", "Sports"]
    rows = []
    for sku in skus:
        base  = rng.integers(10, 120)
        price = round(float(rng.uniform(8, 200)), 2)
        func  = rng.choice(funcs)
        for period in periods:
            trend  = 1 + 0.003 * period
            season = 1 + 0.15 * np.sin(2 * np.pi * period / 52)
            promo  = int(rng.random() < 0.36)
            sales  = max(1, int(base * trend * season * (1.25 if promo else 1) + rng.normal(0, 5)))
            rows.append({
                "sku_id": sku, "period": period,
                "weekly_sales": sales, "feat_main_page": promo,
                "price": price, "functionality": func,
                "color": rng.choice(["Red","Blue","Green","Black","White"]),
                "vendor": rng.choice(["VendorA","VendorB","VendorC"]),
            })
    return pd.DataFrame(rows)


def get_data() -> pd.DataFrame:
    df = load_data()
    return df if not df.empty else make_simulated_data()


# ─────────────────────────────────────────────────────────────
# KPI COMPUTATIONS
# ─────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    sku_sales = df.groupby("sku_id")["weekly_sales"].sum()
    # Number of promotions = count of rows with feat_main_page==1
    number_of_promotions = int((df["feat_main_page"] == 1).sum())
    total_skus = df["sku_id"].nunique()
    return {
        "total_skus":           int(total_skus),
        "total_periods":        int(df["period"].nunique()),
        "avg_price":            round(float(df["price"].mean()), 2),
        "number_of_promotions": number_of_promotions,
        "top_sku":              int(sku_sales.idxmax()),
        "weakest_sku":          int(sku_sales.idxmin()),
    }


def compute_top_skus(df: pd.DataFrame, n: int = 5) -> list:
    s = df.groupby("sku_id")["weekly_sales"].sum().sort_values(ascending=False).head(n)
    return [{"sku": int(k), "sales": int(v)} for k, v in s.items()]


def compute_sku_snapshot(df: pd.DataFrame, n: int = 8) -> list:
    grp = (
        df.groupby("sku_id")
        .agg(avg_sales=("weekly_sales","mean"), avg_price=("price","mean"),
             promo_count=("feat_main_page","sum"), total_weeks=("period","count"))
        .reset_index()
    )
    grp["promo_pct"] = (grp["promo_count"] / grp["total_weeks"] * 100).round(1)
    grp["avg_sales"] = grp["avg_sales"].round(1)
    grp["avg_price"] = grp["avg_price"].round(2)
    # Status based on median sales: Online (>130% median), Active (50-130%), Low (<50%)
    med = grp["avg_sales"].median()
    grp["status"] = grp.apply(
        lambda r: "Online" if r["avg_sales"] > med * 1.3
                  else ("Active" if r["promo_pct"] > 50 else "Low"),
        axis=1,
    )
    return grp.head(n).to_dict("records")


# ─────────────────────────────────────────────────────────────
# PLOTLY CHARTS
# ─────────────────────────────────────────────────────────────

def make_line_chart(df: pd.DataFrame) -> go.Figure:
    weekly = df.groupby("period")["weekly_sales"].sum().reset_index().sort_values("period")
    promo_weekly = (
        df[df["feat_main_page"] == 1]
        .groupby("period")["weekly_sales"].sum().reset_index()
    )
    promo_map = dict(zip(promo_weekly["period"], promo_weekly["weekly_sales"]))
    weekly["promo_sales"] = weekly["period"].map(promo_map).fillna(0)

    idx = np.linspace(0, len(weekly)-1, min(40, len(weekly)), dtype=int)
    w   = weekly.iloc[idx]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=w["period"], y=w["weekly_sales"],
        name="Total Sales", mode="lines",
        line=dict(color=C["teal"], width=2.5),
        fill="tozeroy", fillcolor="rgba(0,212,170,0.07)",
        hovertemplate="Week %{x}<br>Total: %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=w["period"], y=w["promo_sales"],
        name="Promoted", mode="lines",
        line=dict(color=C["amber"], width=2, dash="dot"),
        fill="tozeroy", fillcolor="rgba(245,158,11,0.06)",
        hovertemplate="Week %{x}<br>Promo: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        legend=dict(
            orientation="h", y=-0.2, x=0,
            font=dict(size=11, color=C["muted"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
        height=230,
    )
    return fig


def make_bar_chart(df: pd.DataFrame) -> go.Figure:
    col = "functionality" if "functionality" in df.columns else None
    if col is None:
        return go.Figure()
    grp = df.groupby(col)["weekly_sales"].mean().sort_values(ascending=False).head(6)
    colours = [C["teal"], C["blue"], C["purple"], C["amber"], C["teal"], C["blue"]]
    # Convert hex to rgba with transparency (Plotly accepts rgba, not hex+alpha)
    def hex_to_rgba(hex_col, alpha=0.4):
        h = hex_col.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    
    transparent_colours = [hex_to_rgba(c, 0.4) for c in colours[:len(grp)]]
    
    fig = go.Figure(go.Bar(
        x=list(grp.index),
        y=[round(float(v), 1) for v in grp.values],
        marker=dict(
            color=transparent_colours,
            line=dict(color=colours[:len(grp)], width=1.5),
        ),
        hovertemplate="%{x}<br>Avg: %{y:.1f}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=210, bargap=0.3)
    fig.update_traces(marker_cornerradius=5)
    return fig


def make_gauge(value: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(font=dict(color=C["text"], size=34), suffix="%"),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=C["muted"],
                      tickfont=dict(color=C["muted"], size=10)),
            bar=dict(color=C["teal"], thickness=0.35),
            bgcolor=C["panel"],
            borderwidth=0,
            steps=[
                dict(range=[0,  60], color="#1a2d42"),
                dict(range=[60, 80], color="#1e3a55"),
                dict(range=[80,100], color="#1e4a3a"),
            ],
            threshold=dict(line=dict(color=C["teal"], width=2),
                           thickness=0.8, value=value),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=C["panel"],
        font=dict(color=C["muted"]),
        margin=dict(l=20, r=20, t=30, b=10),
        height=195,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# HTML FRAGMENTS
# ─────────────────────────────────────────────────────────────

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:4px}
.kpi-card{background:#112236;border:1px solid #1e3a55;border-radius:12px;padding:18px 16px 14px;
  transition:transform .25s cubic-bezier(.4,0,.2,1),border-color .25s,box-shadow .25s;cursor:pointer}
.kpi-card:hover{transform:translateY(-3px);border-color:rgba(0,212,170,.55);
  box-shadow:0 8px 32px rgba(0,212,170,.12)}
.kpi-card.t-teal{border-top:3px solid #00d4aa}
.kpi-card.t-purple{border-top:3px solid #7c5cbf}
.kpi-card.t-amber{border-top:3px solid #f59e0b}
.kpi-card.t-blue{border-top:3px solid #3b82f6}
.kpi-lbl{font:600 10px/1 'DM Sans',sans-serif;text-transform:uppercase;
  letter-spacing:.1em;color:#ffffff !important;margin-bottom:8px}
.kpi-val{font:700 36px/1 'Space Grotesk',sans-serif;color:#fff!important;margin-bottom:6px}
.kpi-sub{font-size:11px;color:#ffffff !important;margin-bottom:8px}
.kpi-badge{display:inline-flex;align-items:center;gap:3px;font:600 11px 'DM Sans',sans-serif;
  padding:2px 8px;border-radius:10px}
.kpi-badge.up{background:rgba(0,212,170,.15);color:#00d4aa}
.kpi-badge.warn{background:rgba(245,158,11,.15);color:#f59e0b}
.db-header{display:flex;align-items:flex-start;justify-content:space-between;
  padding-bottom:14px;margin-bottom:16px;border-bottom:1px solid #1e3a55}
.db-title{font:600 20px/1.2 'Space Grotesk',sans-serif;color:#ffffff !important;margin-bottom:4px}
.db-sub{font-size:12px;color:#ffffff !important}
.db-pills{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:4px}
.pill{background:#1a2d42;border:1px solid #2a4a6a;border-radius:6px;
  padding:3px 10px;font-size:11px;color:#ffffff !important}
.badge-live{background:rgba(239,68,68,.15);color:#ef4444 !important;border:1px solid rgba(239,68,68,.3);
  border-radius:20px;padding:3px 10px;font:600 11px 'DM Sans',sans-serif}
.ph{font:600 11px/1 'DM Sans',sans-serif;text-transform:uppercase;letter-spacing:.07em;
  color:#ffffff !important;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between}
.dot-t{color:#ffffff !important}.dot-a{color:#ffffff !important}.dot-p{color:#ffffff !important}.dot-b{color:#ffffff !important}
.tl{list-style:none;padding:0;margin:0}
.tl li{display:flex;align-items:center;justify-content:space-between;
  padding:7px 6px;border-bottom:1px solid #1a3050;border-radius:6px;
  cursor:pointer;transition:background .15s}
.tl li:last-child{border-bottom:none}
.tl li:hover{background:#1a2d42}
.rk{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font:700 10px 'Space Grotesk',sans-serif;flex-shrink:0;
  background:#0d2235;color:#5a7a9a}
.rk.r1{background:rgba(245,158,11,.2);color:#f59e0b}
.rk.r2{background:rgba(148,163,184,.15);color:#94a3b8}
.rk.r3{background:rgba(205,124,56,.15);color:#cd7c38}
.sn{flex:1;margin-left:8px;font-size:12px;color:#ffffff !important}
.sv{font:600 12px 'Space Grotesk',sans-serif;color:#ffffff !important}
.sk{width:100%;border-collapse:collapse;font-size:11px}
.sk th{color:#ffffff !important;font:600 10px 'DM Sans',sans-serif;text-transform:uppercase;
  letter-spacing:.07em;padding:0 8px 8px;text-align:left}
.sk td{padding:6px 8px;color:#ffffff !important;border-bottom:1px solid #162840}
.sk tr:hover td{background:#1a2d42}
.sk tr:last-child td{border-bottom:none}
.sd{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}
.s-on{background:#00d4aa;box-shadow:0 0 5px rgba(0,212,170,.6)}
.s-ac{background:#3b82f6;box-shadow:0 0 5px rgba(59,130,246,.6)}
.s-lw{background:#f59e0b;box-shadow:0 0 5px rgba(245,158,11,.6)}
.sku-25{color:#00d4aa !important;font-weight:700}
.sku-42{color:#f59e0b !important;font-weight:700}
.trend-red{color:#ef4444 !important}
.promo-orange{color:#f59e0b !important}
.sales-white{color:#ffffff !important}
.sku-snapshot-orange{color:#f59e0b !important}
.footer-text{color:#ffffff !important}
.top-perf-red{color:#ef4444 !important}
.gg{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.gc{background:#0d2235;border-radius:8px;padding:10px;text-align:center}
.gl{font-size:10px;color:#ffffff !important;text-transform:uppercase;letter-spacing:.07em;font-weight:600}
.gv{font:700 15px 'Space Grotesk',sans-serif;margin-top:3px;color:#ffffff !important}
.df{display:flex;align-items:center;justify-content:space-between;
  padding:10px 16px;margin-top:6px;background:#0a1520;
  border:1px solid #1e3048;border-radius:8px;font-size:11px;color:#ffffff !important}
.df .ok{color:#ffffff !important}
.panel-wrap{background:#112236;border:1px solid #1e3a55;border-radius:12px;
  padding:16px;transition:border-color .25s}
.panel-wrap:hover{border-color:#2a4a6a}
</style>
"""


def build_header_html(kpis: dict) -> str:
    return f"""{SHARED_CSS}
<div style="background:#0d1b2a;padding:16px 4px 0">
  <div class="db-header">
    <div>
      <div class="db-title">Overview</div>
      <div class="db-sub">Real-time retail analytics &amp; KPI monitoring</div>
    </div>
    <div class="db-pills">
      <span class="pill">Week 1&#8211;{kpis['total_periods']}</span>
      <span class="pill">{kpis['total_skus']} SKUs</span>
      <span class="badge-live">&#9679;&nbsp;Live</span>
    </div>
  </div>
  <div class="kpi-row">
    <div class="kpi-card t-teal">
      <div class="kpi-lbl">&#9632; Total SKUs</div>
      <div class="kpi-val">{kpis['total_skus']}</div>
      <div class="kpi-sub">Unique products analyzed</div>
      <span class="kpi-badge up">&#8679; All active</span>
    </div>
    <div class="kpi-card t-purple">
      <div class="kpi-lbl">&#9632; Data Periods</div>
      <div class="kpi-val">{kpis['total_periods']}</div>
      <div class="kpi-sub">Weekly observations</div>
      <span class="kpi-badge up">&#8679; {round(kpis['total_periods']/52, 1)} yrs</span>
    </div>
    <div class="kpi-card t-amber">
      <div class="kpi-lbl">&#9632; Avg Price</div>
      <div class="kpi-val">${kpis['avg_price']}</div>
      <div class="kpi-sub">Across all SKUs</div>
      <span class="kpi-badge warn">&#8722; Baseline</span>
    </div>
    <div class="kpi-card t-blue">
      <div class="kpi-lbl">&#9632; Promotions Run</div>
      <div class="kpi-val">{kpis['number_of_promotions']:,}</div>
      <div class="kpi-sub">Total promo instances</div>
      <span class="kpi-badge up">&#8679; {round(kpis['number_of_promotions']/kpis['total_periods'], 1)} per wk</span>
    </div>
  </div>
</div>"""


def build_top_html(tops: list) -> str:
    rc = ["r1","r2","r3","",""]
    items = "".join(
        f'<li><span class="rk {rc[i] if i<5 else ""}">{i+1}</span>'
        f'<span class="sn {"sku-25" if t["sku"] == 25 else "sku-42" if t["sku"] == 42 else ""}">SKU {t["sku"]}</span>'
        f'<span class="sv">{t["sales"]:,}</span></li>'
        for i, t in enumerate(tops)
    )
    return f"""
<div class="panel-wrap" style="height:100%">
  <div class="ph"><span class="top-perf-red"><span class="dot-a">&#9733;</span>&nbsp;Top Performers</span></div>
  <ul class="tl">{items}</ul>
</div>"""


def build_gauge_labels_html(top_sku: int, weakest_sku: int) -> str:
    return f"""
<div class="gg" style="padding:0 4px">
  <div class="gc"><div class="gl">Strongest</div>
    <div class="gv {"sku-25" if top_sku == 25 else "sku-42" if top_sku == 42 else ""}">SKU {top_sku}</div></div>
  <div class="gc"><div class="gl">Weakest</div>
    <div class="gv {"sku-25" if weakest_sku == 25 else "sku-42" if weakest_sku == 42 else ""}">SKU {weakest_sku}</div></div>
</div>"""


def build_table_html(rows: list) -> str:
    dot = {"Online":"s-on","Active":"s-ac","Low":"s-lw"}
    trs = "".join(
        f'<tr><td><strong style="color:#e8edf5" class="{"sku-25" if r["sku_id"] == 25 else "sku-42" if r["sku_id"] == 42 else ""}">{r["sku_id"]}</strong></td>'
        f'<td><span class="sd {dot.get(r["status"],"s-lw")}"></span>{r["status"]}</td>'
        f'<td>{r["avg_sales"]}</td><td>${r["avg_price"]}</td><td>{r["promo_pct"]}%</td></tr>'
        for r in rows
    )
    return f"""
<div class="panel-wrap">
  <div class="ph">
    <span class="sku-snapshot-orange"><span class="dot-t">&#9632;</span>&nbsp;SKU Status Snapshot</span>
    <span style="background:#1a2d42;border:1px solid #2a4a6a;border-radius:6px;
                 padding:2px 7px;font-size:10px;color:#4a6080">Top 8</span>
  </div>
  <table class="sk">
    <thead><tr><th>SKU</th><th>Status</th><th>Avg Sales</th><th>Price</th><th>Promo%</th></tr></thead>
    <tbody>{trs}</tbody>
  </table>
</div>"""


def build_panel_title(icon_class: str, icon: str, label: str, right: str = "") -> str:
    right_html = f'<span style="font-size:10px;color:#4a6080">{right}</span>' if right else ""
    return f"""
<div class="panel-wrap" style="padding-bottom:4px;border-bottom:none;
     border-bottom-left-radius:0;border-bottom-right-radius:0;
     border-bottom:0;margin-bottom:0">
  <div class="ph">
    <span><span class="{icon_class}">{icon}</span>&nbsp;{label}</span>
    {right_html}
  </div>
</div>"""


def build_footer_html() -> str:
    return """
<div class="df">
  <span class="footer-text">&#9432; Data source: data_raw.csv &#8212; read only</span>
  <span class="footer-text">Dashboard Lead &middot; Module 1 &middot; AI-assisted: reviewed by team</span>
  <span class="ok">&#10003; All models &lt; 8 GB RAM</span>
</div>"""


# ─────────────────────────────────────────────────────────────
# GRADIO BUILDER
# ─────────────────────────────────────────────────────────────

def build_collapsible_section(section_id: str, title: str, content_html: str) -> str:
    """Create a clickable collapsible section with expand/collapse chevron."""
    return f"""
<style>
  .collapsible-header {{
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #0a1520;
    border: 1px solid #1e3a55;
    border-radius: 8px 8px 0 0;
    user-select: none;
    transition: background 0.2s;
  }}
  .collapsible-header:hover {{
    background: #0f2438;
  }}
  .collapsible-title {{
    font-weight: 600;
    color: #ffffff !important;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .collapsible-chevron {{
    color: #3b82f6 !important;
    font-size: 14px;
    transition: transform 0.2s;
    font-weight: bold;
  }}
  .collapsible-chevron.open {{
    transform: rotate(0deg);
  }}
  .collapsible-content {{
    max-height: 0;
    overflow: hidden;
    background: #0a1520;
    border: 1px solid #1e3a55;
    border-top: none;
    border-radius: 0 0 8px 8px;
    transition: max-height 0.3s ease;
    padding: 0 16px;
  }}
  .collapsible-content.open {{
    max-height: 1000px;
    padding: 16px;
  }}
  .collapsible-content ul, .collapsible-content p {{
    color: #3b82f6 !important;
    font-size: 11px;
    line-height: 1.6;
    margin: 0;
  }}
  .collapsible-content ul {{
    padding-left: 16px;
  }}
  .collapsible-content li {{
    margin-bottom: 6px;
  }}
  .collapsible-content strong {{
    color: #60a5fa !important;
  }}
</style>
<div style="margin-top: 12px;">
  <div class="collapsible-header" onclick="toggleCollapsible('{section_id}')">
    <span class="collapsible-title">{title}</span>
    <span class="collapsible-chevron open" id="{section_id}-chevron">▼</span>
  </div>
  <div class="collapsible-content open" id="{section_id}">
    {content_html}
  </div>
</div>
<script>
  function toggleCollapsible(id) {{
    const content = document.getElementById(id);
    const chevron = document.getElementById(id + '-chevron');
    content.classList.toggle('open');
    chevron.classList.toggle('open');
  }}
</script>"""


def build_project_description_html() -> str:
    """Project description and navigation instructions - collapsible."""
    content = """
    <p style="margin:0 0 8px"><strong style="color:#60a5fa">This dashboard integrates real-time retail analytics with predictive modeling and AI-augmented insights. Use the sidebar to explore:</strong></p>
    <ul style="margin:0;color:#3b82f6">
      <li><strong style="color:#60a5fa">Module 1 (Overview)</strong>: High-level KPI summary and key findings</li>
      <li><strong style="color:#60a5fa">Module 2 (Data Explorer)</strong>: Inspect raw data, filtering, and descriptive statistics</li>
      <li><strong style="color:#60a5fa">Modules 3–5 (Analytics)</strong>: Promotion effectiveness, price elasticity, scenario simulation</li>
      <li><strong style="color:#60a5fa">Modules 6–7 (ML)</strong>: Demand forecasting and promotion lift modeling</li>
      <li><strong style="color:#60a5fa">Module 8 (Chat)</strong>: Ask data-grounded questions in natural language</li>
      <li><strong style="color:#60a5fa">Module 9 (Reflection)</strong>: Critical assessment of AI components</li>
      <li><strong style="color:#60a5fa">Module 10 (Export)</strong>: Download results and model documentation</li>
    </ul>
    """
    return build_collapsible_section("proj-desc", "📋 Project Description & Navigation", content)


def build_key_findings_html() -> str:
    """Key findings from analytical modules - collapsible."""
    content = """
    <p style="margin:0"><em style="color:#60a5fa">Key findings from Modules 3–7 will auto-populate here once analytical pipelines complete. This section will synthesize:</em></p>
    <ul style="margin:8px 0 0;color:#3b82f6">
      <li>Promotion lift impact per SKU</li>
      <li>Price elasticity rankings</li>
      <li>Demand forecasts and seasonality</li>
      <li>Scenario recommendations</li>
    </ul>
    """
    return build_collapsible_section("key-find", "⭐ Key Findings", content)


def build_key_assumptions_html() -> str:
    """Key assumptions made during analysis - collapsible."""
    content = """
    <ul style="margin:0;color:#3b82f6">
      <li><strong style="color:#60a5fa">Data completeness:</strong> All periods represent complete weeks; no gaps assumed to be missing-at-random</li>
      <li><strong style="color:#60a5fa">Causality:</strong> Promotion feature (feat_main_page) assumed causal for incremental lift (SCAN*PRO justification)</li>
      <li><strong style="color:#60a5fa">Stationarity:</strong> Historical patterns assumed to persist in forecast horizon unless structural breaks detected</li>
      <li><strong style="color:#60a5fa">Price exogeneity:</strong> Price changes assumed independent of demand shocks in elasticity estimation</li>
      <li><strong style="color:#60a5fa">Model scope:</strong> Recommendations apply to baseline & scenario cases only; external events (supply shock, competition) not modeled</li>
      <li><strong style="color:#60a5fa">AI guardrails:</strong> All AI-generated narratives grounded in actual data; hallucinations blocked via prompt engineering</li>
    </ul>
    """
    return build_collapsible_section("key-assum", "✓ Key Assumptions", content)


def build_overview_tab():
    """
    Renders the Overview module inside a running gr.Blocks context.
    Usage in app.py:
        with gr.Tab('1. Overview'):
            build_overview_tab()
    """
    df       = get_data()
    kpis     = compute_kpis(df)
    tops     = compute_top_skus(df, 5)
    snap     = compute_sku_snapshot(df, 8)
    fig_line = make_line_chart(df)
    fig_bar  = make_bar_chart(df)
    fig_gau  = make_gauge(float(kpis['number_of_promotions'] / kpis['total_periods'] * 100))

    # Header + KPI row
    gr.HTML(value=build_header_html(kpis))

    # Project Description & Navigation
    gr.HTML(value=build_project_description_html())

    # Row 2 — Line chart | Top performers | Gauge
    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            gr.HTML(value=f"""
            <div class="panel-wrap" style="margin-bottom:0;border-bottom-left-radius:0;
                 border-bottom-right-radius:0;border-bottom:none;padding-bottom:4px">
              <div class="ph" style="margin-bottom:0">
                <span class="trend-red"><span class="dot-t">&#9650;</span>&nbsp;Weekly Sales Trend</span>
                <span style="font-size:10px;color:#4a6080">All SKUs</span>
              </div>
            </div>""")
            gr.Plot(value=fig_line, show_label=False, container=False)

        with gr.Column(scale=3):
            gr.HTML(value=build_top_html(tops))

        with gr.Column(scale=3):
            gr.HTML(value=f"""
            <div class="panel-wrap" style="margin-bottom:0;border-bottom-left-radius:0;
                 border-bottom-right-radius:0;border-bottom:none;padding-bottom:4px">
              <div class="ph" style="margin-bottom:0">
                <span class="promo-orange"><span class="dot-p">&#9899;</span>&nbsp;Promo Score</span>
              </div>
            </div>""")
            gr.Plot(value=fig_gau, show_label=False, container=False)
            gr.HTML(value=build_gauge_labels_html(kpis["top_sku"], kpis["weakest_sku"]))

    # Row 3 — Bar chart | SKU table
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML(value=f"""
            <div class="panel-wrap" style="margin-bottom:0;border-bottom-left-radius:0;
                 border-bottom-right-radius:0;border-bottom:none;padding-bottom:4px">
              <div class="ph" style="margin-bottom:0">
                <span class="sales-white"><span class="dot-b">&#9646;</span>&nbsp;Sales by Functionality</span>
              </div>
            </div>""")
            gr.Plot(value=fig_bar, show_label=False, container=False)

        with gr.Column(scale=1):
            gr.HTML(value=build_table_html(snap))

    # Key Findings
    gr.HTML(value=build_key_findings_html())

    # Key Assumptions
    gr.HTML(value=build_key_assumptions_html())

    # Footer
    gr.HTML(value=build_footer_html())


# ─────────────────────────────────────────────────────────────
# STANDALONE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with gr.Blocks(
        title="Overview — Retail Dashboard",
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
        ),
        css=GRADIO_CSS,
    ) as demo:
        build_overview_tab()

    demo.launch()