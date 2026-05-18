"""
Main Gradio application — AI-Augmented Retail Analytics Dashboard.

Run:
    python main.py (local)
    python app/main.py (from dashboard dir)
    
Deploy to HF Spaces:
    gradio deploy
"""

import gradio as gr
import os
import sys
from pathlib import Path

# Support both local and HF Spaces environments
current_dir = Path(__file__).parent.parent
app_root = current_dir.parent

# Try GitHub structure first, fallback to HF Spaces
sys.path.insert(0, str(app_root))
sys.path.insert(0, str(current_dir))

# Import modules - works in both environments
try:
    # GitHub structure (dashboard/modules)
    from dashboard.modules import overview
    from dashboard.modules.module_7 import build_module_7_tab
except (ImportError, ModuleNotFoundError):
    # HF Spaces structure (modules)
    from modules import overview
    from modules.module_7 import build_module_7_tab

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

/* ── Module 7 Styling ── */
/* ── Buttons: hover effects ── */
.module7-btn {
    background: linear-gradient(135deg, #1e4d3f 0%, #0a1520 100%) !important;
    border: 1px solid rgba(0, 212, 170, 0.2) !important;
    color: #e8edf5 !important;
    border-radius: 6px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 212, 170, 0.1) !important;
}

.module7-btn:hover {
    background: linear-gradient(135deg, #00d4aa 0%, #1e4d3f 100%) !important;
    border-color: #00d4aa !important;
    color: #0d1b2a !important;
    box-shadow: 0 8px 20px rgba(0, 212, 170, 0.25) !important;
    transform: translateY(-2px) !important;
}

.module7-btn:active {
    transform: translateY(0) !important;
    box-shadow: 0 4px 10px rgba(0, 212, 170, 0.15) !important;
}

/* ── Card containers ── */
.module7-card {
    background: linear-gradient(135deg, #0a1520 0%, #0d2235 100%) !important;
    border: 1px solid #1e3048 !important;
    border-radius: 8px !important;
    padding: 20px !important;
    margin: 10px 0 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

.module7-card:hover {
    border-color: rgba(0, 212, 170, 0.3) !important;
    box-shadow: 0 8px 20px rgba(0, 212, 170, 0.1) !important;
    background: linear-gradient(135deg, #0d2235 0%, #0a3a4a 100%) !important;
}

/* ── Textbox/Summary styling ── */
.module7-summary {
    background: #081120 !important;
    border: 1px solid #1e4d3f !important;
    border-left: 3px solid #00d4aa !important;
    color: #d0d8e0 !important;
    border-radius: 4px !important;
    padding: 12px 16px !important;
    line-height: 1.6 !important;
    font-size: 13px !important;
}

/* ── Dropdown styling ── */
.module7-dropdown {
    background: #0a1520 !important;
    border: 1px solid #1e3048 !important;
    color: #e8edf5 !important;
    border-radius: 6px !important;
}

.module7-dropdown:hover {
    border-color: #00d4aa !important;
    box-shadow: 0 4px 12px rgba(0, 212, 170, 0.1) !important;
}

/* ── Tags/Badges ── */
.module7-badge {
    display: inline-block;
    background: rgba(0, 212, 170, 0.1) !important;
    border: 1px solid rgba(0, 212, 170, 0.3) !important;
    color: #00d4aa !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    margin: 2px 4px !important;
    transition: all 0.2s ease !important;
}

.module7-badge:hover {
    background: rgba(0, 212, 170, 0.2) !important;
    border-color: #00d4aa !important;
    transform: scale(1.05) !important;
}

/* ── Section headers ── */
.module7-section-title {
    color: #00d4aa !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    margin-top: 24px !important;
    margin-bottom: 12px !important;
    border-bottom: 2px solid rgba(0, 212, 170, 0.2) !important;
    padding-bottom: 8px !important;
}

/* ── Download button (primary) ── */
.module7-download-btn {
    background: linear-gradient(135deg, #00d4aa 0%, #00a885 100%) !important;
    border: none !important;
    color: #0d1b2a !important;
    border-radius: 6px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    box-shadow: 0 4px 12px rgba(0, 212, 170, 0.25) !important;
}

.module7-download-btn:hover {
    background: linear-gradient(135deg, #00e6bb 0%, #00d4aa 100%) !important;
    box-shadow: 0 8px 24px rgba(0, 212, 170, 0.35) !important;
    transform: translateY(-3px) !important;
}

/* ── Prose/text color fixes ── */
.module7-card .prose,
.module7-card p,
.module7-card h3,
.module7-card h4 {
    color: #d0d8e0 !important;
}

.module7-card strong {
    color: #00d4aa !important;
}

.module7-card code {
    background: rgba(0, 212, 170, 0.08) !important;
    color: #00d4aa !important;
    padding: 2px 6px !important;
    border-radius: 3px !important;
}
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
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
        ),
        css=APP_CSS,
    )


if __name__ == "__main__":
    main()
