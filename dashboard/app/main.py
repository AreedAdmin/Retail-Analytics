"""
Main Gradio application — AI-Augmented Retail Analytics Dashboard.

Run:
    python -m dashboard.app.main
"""

import gradio as gr
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

from dashboard.modules import overview
from dashboard.modules.data_explorer import build_data_explorer_tab
from dashboard.modules.promotion_effectiveness import build_promotion_effectiveness_tab
from dashboard.modules.price_elasticity import build_price_elasticity_tab
from dashboard.modules.scenario_simulator import build_scenario_simulator_tab
from dashboard.modules.demand_forecasting import build_demand_forecasting_tab
from dashboard.modules.module_7 import build_module_7_tab
from dashboard.modules.module_8_chat import build_module_8_chat_tab
from dashboard.modules.critical_reflection import build_critical_reflection_tab
from dashboard.modules.appendix_export import build_appendix_export_tab

APP_CSS = """
body, .gradio-container, .main, .wrap, .gap {
    background: #0d1b2a !important;
    color: #e8edf5 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.block, .form {
    background: #112236 !important;
    border: 1px solid #1e3a55 !important;
    border-radius: 12px !important;
}
.tab-nav { background: #0d1b2a !important; border-bottom: 1px solid #1e3a55 !important; }
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
.plotly-graph-div { background: #112236 !important; }
footer { display: none !important; }
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AI-Augmented Retail Analytics Dashboard") as app:
        gr.Markdown(
            "# Retail Analytics Dashboard\n"
            "AI-augmented decision support for demand forecasting, promotions, pricing, and scenarios."
        )

        with gr.Tabs():
            with gr.Tab("1 · Overview"):
                overview.build_overview_tab()
            build_data_explorer_tab()
            build_promotion_effectiveness_tab()
            build_price_elasticity_tab()
            build_scenario_simulator_tab()
            build_demand_forecasting_tab()
            build_module_7_tab()
            build_module_8_chat_tab()
            build_critical_reflection_tab()
            build_appendix_export_tab()

    return app


def main():
    app = build_app()
    app.launch(
        debug=True,
        show_error=True,
        css=APP_CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
        ),
    )


if __name__ == "__main__":
    main()
