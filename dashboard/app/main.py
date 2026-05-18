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

from dashboard.modules import (
    overview,
    data_explorer,
    promotion_effectiveness,
    price_elasticity,
    scenario_simulator,
    demand_forecasting,
    promotion_lift_model,
    chat_interface,
    ai_analytics,
    critical_reflection,
    appendix_export,
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS  — dark everything, including sidebar
# ─────────────────────────────────────────────────────────────
APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* ── Palantir-style theme tokens ── dark is the default ── */
:root, body, .gradio-container {
    --bg:            #0a0d13;
    --bg-sidebar:    #070a0f;
    --bg-panel:      #11151d;
    --bg-elev:       #161b24;
    --border:        #1d2430;
    --border-sidebar:#151a22;
    --text:          #d7dde6;
    --text-muted:    #79838f;
    --text-dim:      #49525f;
    --accent:        #4d9bff;
    --accent-soft:   rgba(77,155,255,0.12);
    --accent-line:   rgba(77,155,255,0.45);
    --hover:         #121823;
    --active-bg:     rgba(77,155,255,0.10);
    --scroll-track:  #0a0d13;
    --scroll-thumb:  #232c39;
    --scroll-thumb-h:#33404f;
    --radius:        4px;
}

/* ── light theme overrides ── applied when body.light-theme ── */
body.light-theme, body.light-theme .gradio-container {
    --bg:            #f5f7fa;
    --bg-sidebar:    #ffffff;
    --bg-panel:      #ffffff;
    --bg-elev:       #eef1f6;
    --border:        #dde2ea;
    --border-sidebar:#e6eaf0;
    --text:          #1b2430;
    --text-muted:    #5a6675;
    --text-dim:      #97a1b0;
    --accent:        #2f6fed;
    --accent-soft:   rgba(47,111,237,0.10);
    --accent-line:   rgba(47,111,237,0.40);
    --hover:         #eef2f8;
    --active-bg:     rgba(47,111,237,0.10);
    --scroll-track:  #e9edf4;
    --scroll-thumb:  #c2ccdb;
    --scroll-thumb-h:#a9b6c9;
}

/* ── base background ── */
body, .gradio-container, .main, .wrap, .gap {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    transition: background 0.2s ease, color 0.2s ease;
}

/* ── sidebar column ── */
.sidebar-col, .sidebar-col > .block,
.sidebar-col .form, .sidebar-col .panel {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-sidebar) !important;
    border-radius: 0 !important;
    padding: 0 !important;
}
.sidebar-col { gap: 0 !important; }

/* ── theme toggle button ── */
.theme-toggle button {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font: 500 11px/1 'IBM Plex Mono', monospace !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    margin: 10px 14px 16px !important;
    width: calc(100% - 28px) !important;
    padding: 9px 0 !important;
    transition: all 0.18s ease !important;
}
.theme-toggle button:hover {
    border-color: var(--accent-line) !important;
    color: var(--accent) !important;
    background: var(--accent-soft) !important;
}

/* ── main panels ── */
.block, .form {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
.output-html, .prose { background: transparent !important; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }

/* ── plotly ── */
.plotly-graph-div { background: transparent !important; }

/* ── tabs ── command-bar styling ── */
.tab-nav {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 2px !important;
}
.tab-nav button {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    font: 500 12px/1 'IBM Plex Mono', monospace !important;
    letter-spacing: .03em !important;
    padding: 12px 14px !important;
    transition: all .15s ease !important;
}
.tab-nav button:hover { color: var(--text) !important; background: var(--hover) !important; }
.tab-nav button.selected {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: var(--accent-soft) !important;
}

/* ── Gradio theme-variable bridge ──────────────────────────────
   Gradio renders labels/inputs/tables/markdown with its OWN css vars,
   which stay light → unreadable on the dark canvas. Remap them to our
   tokens so all chrome follows the theme (and the light toggle). */
.gradio-container, body, body.light-theme .gradio-container {
    --body-text-color: var(--text) !important;
    --body-text-color-subdued: var(--text-muted) !important;
    --block-title-text-color: var(--text) !important;
    --block-label-text-color: var(--text-muted) !important;
    --block-info-text-color: var(--text-muted) !important;
    --block-background-fill: var(--bg-panel) !important;
    --block-border-color: var(--border) !important;
    --border-color-primary: var(--border) !important;
    --background-fill-primary: var(--bg) !important;
    --background-fill-secondary: var(--bg-panel) !important;
    --input-background-fill: var(--bg-elev) !important;
    --input-border-color: var(--border) !important;
    --input-placeholder-color: var(--text-dim) !important;
    --input-text-color: var(--text) !important;
    --color-accent: var(--accent) !important;
    --color-accent-soft: var(--accent-soft) !important;
    --link-text-color: var(--accent) !important;
    --table-text-color: var(--text) !important;
    --table-even-background-fill: var(--bg-panel) !important;
    --table-odd-background-fill: var(--bg-elev) !important;
    --table-border-color: var(--border) !important;
    --button-secondary-background-fill: var(--bg-elev) !important;
    --button-secondary-text-color: var(--text) !important;
    --neutral-950: var(--text) !important;
}
/* explicit fallbacks for elements that ignore the vars */
.gradio-container, .gradio-container .prose,
.gradio-container .prose *, .gradio-container p,
.gradio-container li, .gradio-container span,
.gradio-container .md, .gradio-container h1, .gradio-container h2,
.gradio-container h3, .gradio-container h4 { color: var(--text); }
.gradio-container label, .gradio-container .label-wrap span,
.gradio-container .block-title, .gradio-container .gr-box label,
span[data-testid="block-info"] { color: var(--text-muted) !important; }
.gradio-container input, .gradio-container textarea,
.gradio-container select, .gradio-container .gr-text-input {
    color: var(--text) !important;
    background: var(--bg-elev) !important;
}
.gradio-container table td, .gradio-container table th {
    color: var(--text) !important; border-color: var(--border) !important;
}
.gradio-container .tab-nav + div, .gradio-container .tabitem {
    background: var(--bg) !important;
}
/* once the sidebar nav is wired, it becomes the sole navigation */
body.sb-wired .tab-nav { display: none !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: var(--scroll-track); }
::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--scroll-thumb-h); }

footer { display: none !important; }

/* ── Gradio 6 white-gap fix ──────────────────────────────────────────
   Gradio 6 renamed/restructured its DOM, so the dark rules above miss
   several structural wrappers and the default white shows through in
   the gaps between cards. Paint only the LAYOUT containers (not widgets
   or charts) with the theme background; var(--bg) still flips for the
   light theme. */
html, gradio-app, .gradio-container,
.gradio-container .main, .main, .wrap, .contain, .app, .fillable,
.tabs, .tabitem, .tab-container, .tabitem > .gap,
.column, .row, .gap {
    background-color: var(--bg) !important;
}
.gradio-container { max-width: 100% !important; }
"""

# ─────────────────────────────────────────────────────────────
# SIDEBAR HTML  (replaces the Gradio Markdown/Button approach)
# ─────────────────────────────────────────────────────────────
SIDEBAR_HTML = """
<style>
.sb { background:var(--bg-sidebar); min-height:100vh; padding:0 0 8px;
  border-right:1px solid var(--border-sidebar);
  font-family:'Inter',system-ui,sans-serif; }

/* brand block */
.sb-brand { display:flex; align-items:center; gap:11px; padding:18px 16px 16px;
  border-bottom:1px solid var(--border-sidebar); position:relative; }
.sb-brand::after { content:''; position:absolute; left:0; right:0; bottom:-1px;
  height:1px; background:linear-gradient(90deg,var(--accent-line),transparent 70%); }
.sb-mark { width:26px; height:26px; flex:none; position:relative; }
.sb-mark i { position:absolute; display:block; box-sizing:border-box; }
.sb-mark i:nth-child(1){ width:16px;height:16px;left:0;top:0;
  border:1.5px solid var(--accent); }
.sb-mark i:nth-child(2){ width:16px;height:16px;right:0;bottom:0;
  background:var(--accent); opacity:.85; }
.sb-name { font:700 13px/1.1 'Space Grotesk',sans-serif; color:var(--text);
  letter-spacing:.02em; }
.sb-sub  { font:500 9px/1.2 'IBM Plex Mono',monospace; color:var(--text-dim);
  text-transform:uppercase; letter-spacing:.16em; margin-top:3px; }

/* section divider */
.sb-sect { display:flex; align-items:center; gap:8px; padding:16px 16px 7px; }
.sb-sect span { font:600 9px/1 'IBM Plex Mono',monospace; color:var(--text-dim);
  text-transform:uppercase; letter-spacing:.18em; white-space:nowrap; }
.sb-sect hr { flex:1; border:none; border-top:1px solid var(--border-sidebar); margin:0; }

/* nav item */
.sb-item { display:flex; align-items:center; gap:11px; padding:8px 16px 8px 14px;
  color:var(--text-muted); border-left:2px solid transparent;
  cursor:pointer; transition:all .15s ease; text-decoration:none;
  user-select:none; -webkit-tap-highlight-color:transparent; }
.sb-item:hover { color:var(--text); background:var(--hover);
  border-left-color:var(--accent-line); }
.sb-idx { font:600 10px/1 'IBM Plex Mono',monospace; color:var(--text-dim);
  width:18px; text-align:right; flex:none; }
.sb-label { font:500 12.5px/1.2 'Inter',sans-serif; letter-spacing:.01em; flex:1; }
.sb-item:hover .sb-idx { color:var(--accent); }

.sb-item.active { color:var(--text); background:var(--active-bg);
  border-left-color:var(--accent); }
.sb-item.active .sb-idx { color:var(--accent); }
.sb-item.active .sb-label { font-weight:600; }

.sb-item.soon { opacity:.45; }
.sb-tag { font:600 8px/1 'IBM Plex Mono',monospace; color:var(--text-dim);
  border:1px solid var(--border); border-radius:2px; padding:3px 5px;
  text-transform:uppercase; letter-spacing:.1em; }

/* status footer */
.sb-foot { margin:18px 16px 0; padding-top:14px;
  border-top:1px solid var(--border-sidebar);
  font:500 9.5px/1.7 'IBM Plex Mono',monospace; color:var(--text-dim);
  text-transform:uppercase; letter-spacing:.1em; }
.sb-foot .dot { display:inline-block; width:6px; height:6px; border-radius:50%;
  background:var(--accent); margin-right:7px; vertical-align:middle;
  box-shadow:0 0 0 3px var(--accent-soft); }
.sb-foot b { color:var(--text-muted); font-weight:600; }
</style>
<div class="sb">
  <div class="sb-brand">
    <div class="sb-mark"><i></i><i></i></div>
    <div>
      <div class="sb-name">RETAIL&middot;ANALYTICS</div>
      <div class="sb-sub">AI Intelligence Console</div>
    </div>
  </div>

  <div class="sb-sect"><span>Workspace</span><hr></div>
  <a class="sb-item active" data-idx="0"><span class="sb-idx">01</span><span class="sb-label">Overview</span></a>
  <a class="sb-item" data-idx="1"><span class="sb-idx">02</span><span class="sb-label">Data Explorer</span></a>

  <div class="sb-sect"><span>Analytics</span><hr></div>
  <a class="sb-item" data-idx="2"><span class="sb-idx">03</span><span class="sb-label">Promotion Effectiveness</span></a>
  <a class="sb-item" data-idx="3"><span class="sb-idx">04</span><span class="sb-label">Price Elasticity</span></a>
  <a class="sb-item" data-idx="4"><span class="sb-idx">05</span><span class="sb-label">Scenario Simulator</span></a>

  <div class="sb-sect"><span>Machine Learning</span><hr></div>
  <a class="sb-item" data-idx="5"><span class="sb-idx">06</span><span class="sb-label">Demand Forecasting</span></a>
  <a class="sb-item" data-idx="6"><span class="sb-idx">07</span><span class="sb-label">Promotion Lift Model</span></a>

  <div class="sb-sect"><span>Intelligence</span><hr></div>
  <a class="sb-item" data-idx="7"><span class="sb-idx">08</span><span class="sb-label">AI Assistant</span></a>
  <a class="sb-item" data-idx="8"><span class="sb-idx">AI</span><span class="sb-label">AI Analytics</span></a>

  <div class="sb-sect"><span>System</span><hr></div>
  <a class="sb-item" data-idx="9"><span class="sb-idx">09</span><span class="sb-label">Critical Reflection</span></a>
  <a class="sb-item" data-idx="10"><span class="sb-idx">10</span><span class="sb-label">Appendix &amp; Export</span></a>

  <div class="sb-foot">
    <div><span class="dot"></span><b>System Online</b></div>
    <div>44 SKUs &middot; 10 Modules + AI Ops</div>
    <div>Build v1.0 &middot; AI Grounded</div>
  </div>
</div>
"""


# ─────────────────────────────────────────────────────────────
# APP BUILDER
# ─────────────────────────────────────────────────────────────

# JS: attach a real DOM click listener to the theme button. Run at
# app.load (with retry, idempotent) because Gradio 6 / HF Spaces does not
# reliably bind Button.click(js=...) for JS-only events.
THEME_TOGGLE_JS = """
() => {
    const bind = () => {
        const btn = document.querySelector('.theme-toggle button');
        if (!btn) return false;
        if (btn.dataset.raThemeWired) return true;
        btn.dataset.raThemeWired = '1';
        btn.addEventListener('click', () => {
            const light = document.body.classList.toggle('light-theme');
            try { localStorage.setItem('ra-theme', light ? 'light' : 'dark'); }
            catch (e) {}
        });
        return true;
    };
    if (!bind()) {
        let n = 0;
        const t = setInterval(() => { if (bind() || ++n > 50) clearInterval(t); }, 150);
    }
}
"""

# Light-only app: always apply the light theme on load. (The dark theme /
# toggle were removed — light matches Gradio's default surfaces, which
# eliminates the white-gap mismatch.)
THEME_RESTORE_JS = """
() => { document.body.classList.add('light-theme'); }
"""

# JS: turn the static sidebar into real navigation. Sidebar item order
# matches the gr.Tabs order 1:1, so item data-idx N drives tab button N.
# Retries because Gradio renders the tab bar asynchronously.
SIDEBAR_NAV_JS = """
() => {
    const wire = () => {
        const tabs = document.querySelectorAll('.tab-nav button');
        const items = document.querySelectorAll('.sb-item[data-idx]');
        if (tabs.length < items.length || !items.length) return false;
        const setActive = (i) => {
            document.querySelectorAll('.sb-item').forEach(
                x => x.classList.remove('active'));
            const it = document.querySelector('.sb-item[data-idx="'+i+'"]');
            if (it) it.classList.add('active');
        };
        items.forEach(it => {
            const i = parseInt(it.getAttribute('data-idx'), 10);
            it.onclick = () => {
                const b = document.querySelectorAll('.tab-nav button')[i];
                if (b) b.click();
                setActive(i);
                const main = document.querySelector('.tabitem')
                          || document.querySelector('.main');
                if (main && main.scrollIntoView) main.scrollIntoView();
            };
        });
        tabs.forEach((b, bi) => b.addEventListener('click', () => setActive(bi)));
        document.body.classList.add('sb-wired');
        return true;
    };
    if (!wire()) {
        let n = 0;
        const t = setInterval(() => {
            if (wire() || ++n > 50) clearInterval(t);
        }, 150);
    }
}
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AI-Augmented Retail Analytics Dashboard") as app:

        with gr.Row(elem_classes=["full-row"]):

            # ── SIDEBAR ──
            with gr.Column(scale=1, min_width=240, elem_classes=["sidebar-col"]):
                gr.HTML(value=SIDEBAR_HTML)
                # (Theme toggle removed — the app is light-only.)

            # ── MAIN CONTENT ──
            # One tab bar; each module owns its own gr.Tab (no double nesting).
            # Modules 4 (Price Elasticity) & 5 (Scenario Simulator) pending.
            with gr.Column(scale=5):
                with gr.Tabs():
                    # overview.build_overview_tab() does NOT open its own
                    # gr.Tab (unlike the others) — it must be wrapped here.
                    with gr.Tab("1. Overview"):
                        overview.build_overview_tab()
                    data_explorer.build_data_explorer_tab()
                    promotion_effectiveness.build_promotion_effectiveness_tab()
                    price_elasticity.build_price_elasticity_tab()
                    scenario_simulator.build_scenario_simulator_tab()
                    demand_forecasting.build_demand_forecasting_tab()
                    promotion_lift_model.build_promotion_lift_model_tab()
                    chat_interface.build_chat_tab()
                    ai_analytics.build_ai_analytics_tab()
                    critical_reflection.build_critical_reflection_tab()
                    appendix_export.build_appendix_export_tab()

        # Restore saved theme + wire the sidebar as the navigation.
        app.load(fn=None, inputs=None, outputs=None, js=THEME_RESTORE_JS)
        app.load(fn=None, inputs=None, outputs=None, js=SIDEBAR_NAV_JS)

    return app


def main():
    app = build_app()
    app.launch(
        debug=True,
        show_error=True,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
        ),
        css=APP_CSS,
    )


if __name__ == "__main__":
    main()
