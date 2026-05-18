# AI-assisted: reviewed by team
"""Module 9 — Critical Reflection."""

import json
from pathlib import Path

import gradio as gr

REPO_ROOT = Path(__file__).resolve().parents[2]
FAILURE_LOG = REPO_ROOT / "ai" / "logs" / "interactions.jsonl"


def _load_failure_examples(max_rows: int = 5) -> list[str]:
    if not FAILURE_LOG.exists():
        return ["No interaction log yet — run the chat or chart summaries to populate examples."]
    examples = []
    try:
        with open(FAILURE_LOG, encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                flags = row.get("guardrail_output") or {}
                unverified = flags.get("unverified_numbers") or []
                if unverified or row.get("event_type") == "refusal":
                    examples.append(
                        f"- **{row.get('event_type', 'query')}:** unverified figures flagged "
                        f"({len(unverified)}) — query: _{str(row.get('user_query', ''))[:80]}_"
                    )
                if len(examples) >= max_rows:
                    break
    except (OSError, json.JSONDecodeError):
        pass
    return examples or ["Log file exists but no failure cases recorded yet."]


def build_critical_reflection_tab():
    failures = _load_failure_examples()

    with gr.Tab("9 · Reflection"):
        gr.Markdown("## Module 9 — Critical Reflection")
        gr.Markdown(
            "Evaluation of GenAI integration for the grading criteria "
            "(prompt engineering, validation, failure cases, honest limitations)."
        )

        gr.Markdown("""
### Prompt engineering
- Prompts live in `ai/prompts/` (`system_chat.txt`, `system_chart_summary.txt`) — not inline strings.
- The LLM receives **structured JSON context** from ML/analytics outputs only; raw CSV rows are never sent.
- Chart summaries are capped at ≤120 words; chat answers follow refusal templates for off-topic or oversized inputs.

### Output validation
- `ai/guardrails/output_validator.py` checks numeric claims against the supplied context payload.
- Responses are labelled **`[Data-grounded]`** or **`[General inference]`** post-generation.
- Unverified numbers are flagged in diagnostics (Module 8) and logged.

### Failure cases (from interaction log)
        """)
        gr.Markdown("\n".join(failures))

        gr.Markdown("""
### Benefits, limitations, and risks
| Aspect | Assessment |
|--------|------------|
| **Benefit** | Plain-language interpretation lowers the barrier for marketing managers |
| **Benefit** | Click-to-summarise ties narratives to specific chart metrics |
| **Limitation** | Elasticity and scenarios use simplified constant-elasticity approximations |
| **Limitation** | Forecast baseline is linear — seasonality may be under-captured until ML Pod A ships |
| **Risk** | Users may over-trust AI labels; diagnostics and Module 9 mitigate but do not eliminate |
| **Risk** | Provider outages fall back to echo/offline mode with reduced usefulness |

### Where AI added value vs. unreliability
- **Reliable:** Summarising ranked lists (lift %, elasticity order) when context JSON matches chart data.
- **Unreliable:** Cross-module synthesis when context files are missing (`_missing` in chat context).
- **Mitigation:** Explicit “I don't have data on this” path in prompts; refusal for off-topic queries.
        """)
