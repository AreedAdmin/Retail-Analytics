# Module 9 — Critical Reflection
# Owner: All teams
# Description: Surfaces the AI guardrail's failure log and documents the
#              prompt-engineering / validation decisions and the honest
#              limitations of the GenAI layer.

import json
from pathlib import Path

import gradio as gr
import pandas as pd

from dashboard.components import ui

FAILURE_LOG = (Path(__file__).resolve().parents[2]
               / "ai" / "services" / "failure_log.jsonl")

REFLECTION_MD = """
### How the AI is kept honest

**Grounding.** Every AI response is built from an `AIContextPayload`
(`ai/services/context_builder.py`) — a JSON snapshot of *explicit numbers*
drawn from the model outputs. The system prompt (`ai/prompts/chat_system.txt`)
forbids citing anything outside that block and mandates the reply say
*"I don't have data on this"* when context is insufficient.

**Post-hoc guardrail.** `ai/services/guardrail.py` re-checks every reply:
every number is matched (with rounding tolerance) against the context, and
the `[Data-grounded]` / `[General inference]` label is *enforced from that
check* — it is derived, not trusted from the model. Flagged replies are
appended to `failure_log.jsonl` (shown above).

**Prompt-engineering decisions.**
- Prompts live as files in `ai/prompts/`, never inline — auditable & versioned.
- Separate templates for chat, single-chart summary and multi-module briefing
  keep each task narrow, which measurably reduces drift.
- Temperature is greedy/deterministic for reproducible grading.

### Honest limitations

- The model-quality figures it cites are themselves imperfect (e.g. the lift
  model's modest out-of-sample R²); a fluent summary can lend false confidence.
- The numeric guardrail catches fabricated *figures*, not flawed *reasoning*
  or mis-attributed causation.
- The free in-Space open model is weaker than frontier APIs; the offline
  fallback is purely extractive (safe but not analytical).
- Forecasts are backtests, not true forward predictions — narratives should
  not be read as future guarantees.
"""


def _load_failures() -> pd.DataFrame:
    if not FAILURE_LOG.exists():
        return pd.DataFrame()
    rows = []
    for line in FAILURE_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            rows.append({
                "module": e.get("module", ""),
                "warnings": "; ".join(e.get("warnings", [])),
                "response_excerpt": e.get("response_excerpt", "")[:160],
            })
        except json.JSONDecodeError:
            continue
    return pd.DataFrame(rows)


def _render():
    df = _load_failures()
    n = len(df)
    cards = ui.kpi_cards([
        ("Logged AI failures", f"{n:,}", "guardrail catches"),
        ("Status", "Clean ✅" if n == 0 else "Review ⚠️",
         "no flagged outputs" if n == 0 else "see table"),
    ])
    table = df if not df.empty else pd.DataFrame(
        {"info": ["No guardrail failures logged yet — "
                  "generate AI summaries to populate this."]})
    return cards, table


def build_critical_reflection_tab():
    """Render Module 9 inside a running gr.Blocks context."""
    with gr.Tab("9. Critical Reflection"):
        gr.HTML(ui.header(
            "Critical Reflection — Module 9",
            "Evidence of AI guardrails working, plus an honest account of "
            "prompt-engineering choices and the limits of this GenAI layer."))

        cards_html, table0 = _render()
        cards = gr.HTML(value=cards_html)
        refresh = gr.Button("↻ Refresh failure log", size="sm")
        table = gr.Dataframe(value=table0, interactive=False, wrap=True,
                             label="Guardrail failure log")
        refresh.click(_render, None, [cards, table])

        gr.Markdown(REFLECTION_MD)


if __name__ == "__main__":
    with gr.Blocks(title="Critical Reflection") as demo:
        build_critical_reflection_tab()
    demo.launch()
