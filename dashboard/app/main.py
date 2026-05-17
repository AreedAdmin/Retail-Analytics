"""
Main Gradio application — AI-Augmented Retail Analytics Dashboard.

Run:
    python main.py
or
    python -m dashboard.app.main
"""

import gradio as gr
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

from dashboard.modules import overview
from dashboard.modules.module_7 import build_module_7_tab

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS  — dark everything, including sidebar
# ─────────────────────────────────────────────────────────────
APP_CSS = """
/* ── base background ── */
body, .gradio-container, .main, .wrap, .gap {
    background: #0d1b2a !important;
    color: #e8edf5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── sidebar column ── */
.sidebar-col, .sidebar-col > .block,
.sidebar-col .form, .sidebar-col .panel {
    background: #0a1520 !important;
    border-right: 1px solid #1e3048 !important;
    border-radius: 0 !important;
}

/* ── nav buttons ── */
.sidebar-col button {
    background: #0a1520 !important;
    color: #8a9bb5 !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    text-align: left !important;
    padding: 9px 16px !important;
    font-size: 13px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.sidebar-col button:hover {
    background: #1a2d42 !important;
    color: #e8edf5 !important;
    border-left-color: rgba(0,212,170,0.3) !important;
}
.sidebar-col button.active-nav {
    color: #00d4aa !important;
    background: #0d2235 !important;
    border-left-color: #00d4aa !important;
}

/* ── markdown in sidebar ── */
.sidebar-col .prose, .sidebar-col p,
.sidebar-col h1, .sidebar-col h2, .sidebar-col h3,
.sidebar-col span {
    color: #8a9bb5 !important;
    background: transparent !important;
}
.sidebar-col .prose em { color: #5a7a9a !important; font-style: italic; }

/* ── section labels in sidebar ── */
.sidebar-col .nav-section {
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #4a6080 !important;
    padding: 12px 16px 4px !important;
    font-weight: 600 !important;
}

/* ── main panels ── */
.block, .form {
    background: #112236 !important;
    border: 1px solid #1e3a55 !important;
    border-radius: 12px !important;
}
.output-html, .prose { background: transparent !important; }

/* ── plotly ── */
.plotly-graph-div { background: #112236 !important; }

/* ── tabs ── */
.tab-nav { background: #0d1b2a !important; border-bottom: 1px solid #1e3a55 !important; }
.tab-nav button {
    background: #0d1b2a !important;
    color: #8a9bb5 !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.tab-nav button.selected {
    color: #00d4aa !important;
    border-bottom: 2px solid #00d4aa !important;
    background: #112236 !important;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1b2a; }
::-webkit-scrollbar-thumb { background: #2a4a6a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a5a7a; }

footer { display: none !important; }
"""

# ─────────────────────────────────────────────────────────────
# SIDEBAR HTML  (replaces the Gradio Markdown/Button approach)
# ─────────────────────────────────────────────────────────────
SIDEBAR_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');
.sb { background:#0a1520; height:100%; padding:16px 0; border-right:1px solid #1e3048; }
.sb-logo { padding:0 16px 16px; border-bottom:1px solid #1e3048; margin-bottom:12px; }
.sb-logo-name { font:600 12px/1 'Space Grotesk',sans-serif; color:#00d4aa;
  text-transform:uppercase; letter-spacing:.08em; display:block; margin-top:6px; }
.sb-logo-sub  { font-size:10px; color:#4a6080; margin-top:2px; display:block; }
.sb-sect { font:600 10px/1 'DM Sans',sans-serif; text-transform:uppercase;
  letter-spacing:.1em; color:#4a6080; padding:12px 16px 5px; }
.sb-item { display:flex; align-items:center; gap:10px; padding:9px 16px;
  font-size:13px; color:#8a9bb5; border-left:3px solid transparent;
  cursor:pointer; transition:all .18s ease; text-decoration:none; }
.sb-item:hover { color:#e8edf5; background:#1a2d42; border-left-color:rgba(0,212,170,.3); }
.sb-item.active { color:#ffffff !important; background:#0d2235; border-left-color:#ffffff; }
.sb-icon { font-size:15px; width:18px; text-align:center; }
</style>
<div class="sb">
  <div class="sb-logo">
    <span class="sb-logo-name">Retail Analytics</span>
    <span class="sb-logo-sub">AI-Augmented Dashboard</span>
  </div>

  <a class="sb-item active">Overview</a>
  <a class="sb-item">Data Explorer</a>

  <div class="sb-sect">Analytics</div>
  <a class="sb-item">Promotions</a>
  <a class="sb-item">Price Elasticity</a>
  <a class="sb-item">Scenarios</a>

  <div class="sb-sect">Machine Learning</div>
  <a class="sb-item">Forecasting</a>
  <a class="sb-item">Promo Lift</a>

  <div class="sb-sect">AI</div>
  <a class="sb-item">Chat Interface</a>
  <a class="sb-item">Reflection</a>
  <a class="sb-item">Export</a>
</div>
"""


# ─────────────────────────────────────────────────────────────
# APP BUILDER
# ─────────────────────────────────────────────────────────────

def build_app() -> gr.Blocks:
    with gr.Blocks(title="AI-Augmented Retail Analytics Dashboard") as app:

        with gr.Row(elem_classes=["full-row"]):

            # ── SIDEBAR ──
            with gr.Column(scale=1, min_width=210, elem_classes=["sidebar-col"]):
                gr.HTML(value=SIDEBAR_HTML)

            # ── MAIN CONTENT ──
            with gr.Column(scale=5):
                overview.build_overview_tab()
                build_module_7_tab()


                # Placeholder tabs for other modules (uncomment as they are built)
                # with gr.Tab("2. Data Explorer"):
                #     data_explorer.build_data_explorer_tab()
                # with gr.Tab("3. Promotion Effectiveness"):
                #     gr.Markdown("### Coming soon — ML Pod B")
                # ...

    return app


def main():
    app = build_app()
    app.launch(
        debug=True,
        show_error=True,
        share=True,
    )
if __name__ == "__main__":
    main()
