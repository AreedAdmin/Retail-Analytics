# Module 2 — Data Explorer
# Owner: Dashboard
# Description: Raw-data inspection over data/data_raw.csv via DataLoader.
#              Filterable table, per-SKU statistics, column dictionary.
#              Pure consumer — no modelling.

import gradio as gr
import pandas as pd

from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.components import ui

COLUMN_DICT = [
    ("period", "Week start date (normalised from 'week')."),
    ("sku_id", "Product identifier (normalised from 'sku')."),
    ("demand_units", "Units sold that week (normalised from 'weekly_sales')."),
    ("feat_main_page", "Promotion flag — featured on the main page that week."),
    ("color", "Product colour attribute."),
    ("price", "Unit price for the week."),
    ("vendor", "Vendor identifier."),
    ("functionality", "Product category / functionality label."),
]

PAGE_SIZE = 25


def _page(df: pd.DataFrame, sku, page: int):
    """Return one page of the (optionally SKU-filtered) table + status text."""
    view = df if sku in (None, "All") else df[df["sku_id"] == sku]
    n = len(view)
    pages = max(1, (n + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(int(page), pages))
    start = (page - 1) * PAGE_SIZE
    chunk = view.iloc[start:start + PAGE_SIZE].copy()
    status = f"Showing {start + 1:,}–{min(start + PAGE_SIZE, n):,} of {n:,} rows · page {page}/{pages}"
    return chunk, status, page, pages


def build_data_explorer_tab():
    """Render Module 2 inside a running gr.Blocks context."""
    with gr.Tab("2. Data Explorer"):
        try:
            loader = get_data_loader()
            df = loader.get_normalized_data()
            stats = loader.get_summary_stats()
            sku_stats = loader.get_sku_stats().reset_index()
        except Exception as e:
            gr.HTML(ui.warn(f"⚠️ Could not load data: {e}"))
            return

        gr.HTML(ui.header(
            "Data Explorer — Module 2",
            "Inspect the raw weekly panel that every model and KPI is built "
            "from. Filter by SKU, page through records, and review per-SKU "
            "summary statistics."))

        gr.HTML(ui.kpi_cards([
            ("Records", f"{stats['num_records']:,}", "weekly rows"),
            ("SKUs", f"{stats['num_skus']:,}", "unique products"),
            ("Periods", f"{stats['num_periods']:,}", "weeks covered"),
            ("Promotions", f"{int(stats['num_promotions']):,}", "featured SKU-weeks"),
            ("Avg price", f"{stats['avg_price']:,.2f}", "across all rows"),
        ]))

        sku_choices = ["All"] + loader.get_sku_list()
        with gr.Row():
            sku_dd = gr.Dropdown(sku_choices, value="All", label="Filter by SKU",
                                 scale=2)
            prev_btn = gr.Button("← Prev", scale=1)
            next_btn = gr.Button("Next →", scale=1)
        status = gr.Markdown()

        chunk, status_txt, p0, _ = _page(df, "All", 1)
        page_state = gr.State(1)
        status.value = status_txt
        table = gr.Dataframe(value=chunk, interactive=False, wrap=True,
                             label="Raw records")

        def _refresh(sku, page):
            chunk, txt, page, _ = _page(df, sku, page)
            return chunk, txt, page

        sku_dd.change(lambda s: _refresh(s, 1), sku_dd,
                      [table, status, page_state])
        prev_btn.click(lambda s, p: _refresh(s, p - 1),
                       [sku_dd, page_state], [table, status, page_state])
        next_btn.click(lambda s, p: _refresh(s, p + 1),
                       [sku_dd, page_state], [table, status, page_state])

        with gr.Accordion("Per-SKU summary statistics", open=False):
            gr.Dataframe(value=sku_stats, interactive=False, wrap=True,
                         label="Aggregates by SKU")

        with gr.Accordion("Column dictionary", open=False):
            gr.HTML(ui.list_panel(
                "Columns (normalised schema)",
                [f"<span>{c}</span><span style='color:var(--text-muted);"
                 f"font-weight:400;text-align:right;max-width:70%'>{d}</span>"
                 for c, d in COLUMN_DICT]))


if __name__ == "__main__":
    with gr.Blocks(title="Data Explorer") as demo:
        build_data_explorer_tab()
    demo.launch()
