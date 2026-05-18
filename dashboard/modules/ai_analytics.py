# Module — AI Analytics
# Owner: AI Pod
# Description: Observability for the GenAI layer. Categorises the prompts
#              users send and reports AI performance (TTFT, TPS, latency,
#              success rate) by category / backend / source. Pure consumer
#              of ai/services/telemetry_log.jsonl (written by every AI call).

import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from ai.services import telemetry
from dashboard.components import ui

_PERF = {"ttft_ms": "TTFT (ms)", "total_ms": "Latency (ms)",
         "tps": "Tokens/sec"}


def _kpis(s: dict) -> str:
    o = s.get("overall", {})
    if not o.get("n_calls"):
        return ui.warn(
            "No AI calls recorded yet.<br>Use the <b>AI Assistant</b> "
            "(or any click-to-summarise / narrative button), then press "
            "<b>Refresh</b> here.")
    ttft = o.get("median_ttft_ms")
    return ui.kpi_cards([
        ("AI calls", f"{o['n_calls']:,}", "logged"),
        ("Success rate", f"{o.get('success_rate', 0):.0f}%", "non-fallback"),
        ("Median TTFT", f"{ttft:,.0f} ms" if ttft else "n/a",
         "time to first token"),
        ("Avg TPS", f"{o.get('avg_tps') or 0:,.1f}", "tokens / second"),
        ("Median latency", f"{o.get('median_total_ms') or 0:,.0f} ms",
         "end-to-end"),
    ])


def _category_bar(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if df.empty or "category" not in df:
        fig.update_layout(**ui.plotly_layout(330))
        return fig
    vc = df["category"].value_counts()
    fig.add_trace(go.Bar(
        x=vc.values, y=vc.index, orientation="h",
        marker_color=ui.ACCENT,
        hovertemplate="%{y}<br>%{x} prompts<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        330, xaxis_title="Prompts", yaxis_title=None))
    return fig


def _perf_by(df: pd.DataFrame, dim: str, metric: str) -> go.Figure:
    fig = go.Figure()
    if df.empty or dim not in df:
        fig.update_layout(**ui.plotly_layout(330))
        return fig
    s = (df.assign(_m=pd.to_numeric(df[metric], errors="coerce"))
         .dropna(subset=["_m"]).groupby(dim)["_m"].mean().sort_values())
    if s.empty:
        fig.update_layout(**ui.plotly_layout(330))
        return fig
    fig.add_trace(go.Bar(
        x=s.index.astype(str), y=s.values, marker_color=ui.ACCENTS[1],
        hovertemplate="%{x}<br>%{y:.1f}<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        330, xaxis_title=dim.title(), yaxis_title=_PERF[metric]))
    return fig


def _refresh(metric_label: str):
    df = telemetry.load_events()
    s = telemetry.summary_stats(df)
    metric = next(k for k, v in _PERF.items() if v == metric_label)
    recent = pd.DataFrame(
        {"info": ["No AI calls recorded yet."]}) if df.empty else (
        df.sort_values("timestamp", ascending=False)
          .head(40)[["timestamp", "source", "category", "backend",
                      "ttft_ms", "tps", "total_ms", "success",
                      "prompt_excerpt"]])
    return (_kpis(s), _category_bar(df),
            _perf_by(df, "category", metric), recent)


def build_ai_analytics_tab():
    """Render the AI Analytics module inside a running gr.Blocks context."""
    with gr.Tab("AI Analytics"):
        gr.HTML(ui.header(
            "AI Analytics",
            "Prompt-mix and live performance of the GenAI layer. Every AI "
            "call logs its category and timing (TTFT = time-to-first-token, "
            "TPS = tokens/sec; native timing on the Ollama backend)."))

        s0 = telemetry.summary_stats()
        df0 = telemetry.load_events()
        kpis = gr.HTML(value=_kpis(s0))
        refresh = gr.Button("↻ Refresh telemetry", size="sm",
                            variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Prompt categories")
                cat = gr.Plot(value=_category_bar(df0), show_label=False,
                              container=False)
            with gr.Column():
                gr.Markdown("#### Performance by category")
                metric_dd = gr.Dropdown(
                    list(_PERF.values()), value="Latency (ms)",
                    label="Metric", interactive=True)
                perf = gr.Plot(
                    value=_perf_by(df0, "category", "total_ms"),
                    show_label=False, container=False)

        gr.Markdown("#### Recent AI calls")
        recent0 = (pd.DataFrame({"info": ["No AI calls recorded yet."]})
                   if df0.empty else df0.sort_values(
                       "timestamp", ascending=False).head(40))
        table = gr.Dataframe(value=recent0, interactive=False, wrap=True)

        refresh.click(lambda m: _refresh(m), metric_dd,
                      [kpis, cat, perf, table])
        metric_dd.change(lambda m: _refresh(m), metric_dd,
                         [kpis, cat, perf, table])


if __name__ == "__main__":
    with gr.Blocks(title="AI Analytics") as demo:
        build_ai_analytics_tab()
    demo.launch()
