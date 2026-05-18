# AI-assisted: reviewed by team
"""Module 2 — Data Explorer."""

import gradio as gr
import pandas as pd

from dashboard.analytics.common.data_loader import get_data_loader
from dashboard.analytics.common.kpi_calculator import get_sku_summary_stats


def build_data_explorer_tab():
    loader = get_data_loader()
    df = loader.get_normalized_data()
    summary = loader.get_summary_stats()
    sku_stats = get_sku_summary_stats(df)

    with gr.Tab("2 · Data Explorer"):
        gr.Markdown("## Module 2 — Data Explorer")
        gr.Markdown(
            "Inspect the raw retail dataset, column definitions, descriptive statistics, "
            "and data-quality checks. Source: `data/data_raw.csv` (read-only)."
        )

        gr.Markdown(
            f"**Dataset:** {summary['num_records']:,} rows · "
            f"{summary['num_skus']} SKUs · {summary['num_periods']} weeks · "
            f"{summary['num_promotions']:,} promotion instances"
        )

        with gr.Accordion("Column dictionary", open=False):
            gr.Markdown("""
| Column | Type | Description |
|--------|------|-------------|
| `week_date` | date | Week start date |
| `period` | int | Numeric week index (1…N) |
| `sku_id` | int | Product identifier |
| `demand_units` | float | Weekly units sold |
| `feat_main_page` | bool | Front-page promotion flag |
| `price` | float | Unit price |
| `color` | str | Product colour |
| `vendor` | int | Vendor code |
| `functionality` | str | Product category |
            """)

        with gr.Row():
            sku_filter = gr.Dropdown(
                choices=["All"] + [str(s) for s in sorted(df["sku_id"].unique())],
                value="All",
                label="Filter by SKU",
            )
            promo_filter = gr.Radio(
                choices=["All", "Promoted only", "Non-promoted only"],
                value="All",
                label="Promotion filter",
            )

        preview_df = gr.Dataframe(
            value=df.head(50),
            label="Data preview (paginated)",
            interactive=False,
        )
        sku_stats_df = gr.Dataframe(
            value=sku_stats,
            label="Per-SKU descriptive statistics",
            interactive=False,
        )

        missing = df.isnull().sum()
        outlier_note = (
            f"Missing values: {int(missing.sum())} total across columns. "
            f"Demand range {summary['demand_range']['min']:.0f}–"
            f"{summary['demand_range']['max']:.0f} units; "
            f"price ${summary['price_range']['min']:.2f}–${summary['price_range']['max']:.2f}."
        )
        gr.Markdown(f"**Data quality:** {outlier_note}")

        def filter_table(sku, promo):
            out = df.copy()
            if sku != "All":
                out = out[out["sku_id"] == int(sku)]
            if promo == "Promoted only":
                out = out[out["feat_main_page"] == True]  # noqa: E712
            elif promo == "Non-promoted only":
                out = out[out["feat_main_page"] == False]  # noqa: E712
            return out.head(100)

        sku_filter.change(filter_table, [sku_filter, promo_filter], preview_df)
        promo_filter.change(filter_table, [sku_filter, promo_filter], preview_df)
