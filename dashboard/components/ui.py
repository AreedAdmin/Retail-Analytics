"""
Reusable, theme-aware UI helpers.

Everything here renders with the CSS custom properties defined in
dashboard/app/main.py (var(--bg-panel), var(--text), ...), so components
follow the global light/dark toggle automatically. Plotly figures use
transparent backgrounds so the panel colour shows through in either theme.
"""

from __future__ import annotations

from typing import List, Tuple

import plotly.graph_objects as go

# Accent palette — readable on both light and dark panels.
ACCENT = "#00b894"
ACCENTS = ["#00b894", "#3b82f6", "#f59e0b", "#7c5cbf", "#ef4444"]

CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');
.ui-title{font:600 20px/1.2 'Space Grotesk',sans-serif;color:var(--text);margin:2px 0 4px}
.ui-note{font-size:12.5px;color:var(--text-muted);margin-bottom:10px;line-height:1.5}
.ui-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:6px 0 14px}
.ui-card{background:var(--bg-panel);border:1px solid var(--border);border-radius:12px;
  padding:15px 14px;border-top:3px solid var(--accent)}
.ui-lbl{font:600 10px/1 'DM Sans',sans-serif;text-transform:uppercase;
  letter-spacing:.1em;color:var(--text-muted);margin-bottom:8px}
.ui-val{font:700 26px/1 'Space Grotesk',sans-serif;color:var(--text)}
.ui-sub{font-size:11px;color:var(--text-muted);margin-top:6px}
.ui-warn{background:var(--bg-panel);border:1px solid var(--border);border-radius:12px;
  padding:22px;color:var(--text);font-size:13px;line-height:1.6}
.ui-list{background:var(--bg-panel);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.ui-list-row{display:flex;justify-content:space-between;padding:8px 13px;
  border-bottom:1px solid var(--border);font-size:12px;color:var(--text)}
.ui-list-row span:first-child{color:var(--text);font-weight:600}
.ui-list-hd{font:600 10px/1 'DM Sans',sans-serif;text-transform:uppercase;
  letter-spacing:.1em;color:var(--accent);padding:11px 13px}
</style>
"""


def warn(message_html: str) -> str:
    """A styled warning/empty-state panel."""
    return CARD_CSS + f'<div class="ui-warn">{message_html}</div>'


def header(title: str, note: str = "") -> str:
    note_html = f'<div class="ui-note">{note}</div>' if note else ""
    return CARD_CSS + f'<div class="ui-title">{title}</div>{note_html}'


def kpi_cards(cards: List[Tuple[str, str, str]]) -> str:
    """cards = [(label, value, subtitle), ...] -> KPI card grid HTML."""
    items = "".join(
        f'<div class="ui-card" style="border-top-color:{ACCENTS[i % len(ACCENTS)]}">'
        f'<div class="ui-lbl">{lbl}</div><div class="ui-val">{val}</div>'
        f'<div class="ui-sub">{sub}</div></div>'
        for i, (lbl, val, sub) in enumerate(cards)
    )
    return CARD_CSS + f'<div class="ui-row">{items}</div>'


def list_panel(title: str, rows: List[str]) -> str:
    """A compact bordered list panel; each row is pre-rendered <span> HTML."""
    body = "".join(f'<div class="ui-list-row">{r}</div>' for r in rows)
    return (CARD_CSS + f'<div class="ui-list"><div class="ui-list-hd">{title}'
            f'</div>{body}</div>')


def plotly_layout(height: int = 360, **extra) -> dict:
    """
    Transparent-background Plotly layout so charts adapt to light/dark.
    Mid-grey text/grid reads acceptably on both panel colours.
    """
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8a9bb5", size=11),
        margin=dict(l=12, r=12, t=12, b=12),
        height=height,
        xaxis=dict(gridcolor="rgba(128,140,165,0.22)",
                   linecolor="rgba(128,140,165,0.35)",
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(128,140,165,0.22)",
                   linecolor="rgba(128,140,165,0.35)",
                   tickfont=dict(size=10)),
        legend=dict(orientation="h", y=-0.18, x=0,
                    font=dict(size=11, color="#8a9bb5"),
                    bgcolor="rgba(0,0,0,0)"),
    )
    base.update(extra)
    return base


def empty_fig(height: int = 360) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(**plotly_layout(height))
    return fig
