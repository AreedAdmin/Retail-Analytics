# AI-assisted: reviewed by [name]
"""
Module 8 AI Chat tab — sole Gradio entry point for the AI chat panel.

build_module_8_tab() constructs the gr.Tab("8 · AI Chat") block.
Called by dashboard/modules/module_8_chat.py.
"""
import uuid
import gradio as gr

from ai.config.settings import LLM_PROVIDER, OLLAMA_MODEL, BEDROCK_MODEL
from ai.providers import get_provider
from ai.services.chat_service import answer_question


# ── Example queries from deliverable.md §8a ──────────────────────────────────

_EXAMPLE_QUERIES: list[str] = [
    "Which SKUs should I prioritise for promotion next quarter?",
    "What happens to total revenue if I reduce prices by 10% across all SKUs?",
    "Which products are most at risk of demand decline?",
    "Is the promotion for SKU 4 generating enough incremental sales to justify the discount?",
]


def _get_model_label() -> str:
    """Return a human-readable provider · model string."""
    if LLM_PROVIDER == "ollama":
        return f"Provider: ollama · Model: {OLLAMA_MODEL}"
    if LLM_PROVIDER == "bedrock":
        return f"Provider: bedrock · Model: {BEDROCK_MODEL}"
    return "Provider: echo · Model: echo-v1 (offline fallback)"


def build_module_8_tab() -> None:
    """Build the Gradio '8 · AI Chat' tab inside the current Blocks context."""
    session_id = uuid.uuid4().hex[:8]

    with gr.Tab("8 · AI Chat"):
        gr.Markdown("## Module 8 — AI Chat Interface")
        gr.Markdown(
            "Ask plain-English questions about the dashboard's retail analytics outputs. "
            "All answers are grounded in pre-computed model outputs — the AI never sees raw data rows. "
            "Every response is labelled **[Data-grounded]** or **[General inference]**."
        )

        # ── Input row ────────────────────────────────────────────
        question_box = gr.Textbox(
            label="Ask a question",
            lines=3,
            placeholder="e.g. Which SKUs should I prioritise for promotion next quarter?",
        )
        with gr.Row():
            ask_btn   = gr.Button("Ask", variant="primary")
            clear_btn = gr.Button("Clear")

        # ── Answer panel ─────────────────────────────────────────
        answer_box = gr.Markdown(value="")

        # ── Diagnostics accordion ────────────────────────────────
        with gr.Accordion("Diagnostics", open=False):
            diag_box = gr.Markdown(value="_No query yet._")

        # ── Example question chips ───────────────────────────────
        gr.Markdown("**Example questions:**")
        with gr.Row():
            example_btns = [
                gr.Button(q, size="sm", variant="secondary")
                for q in _EXAMPLE_QUERIES
            ]

        # ── Provider label ───────────────────────────────────────
        gr.Markdown(f"_{_get_model_label()}_")

        # ── Event handlers ────────────────────────────────────────

        def on_ask(question: str):
            if not question.strip():
                return "Please enter a question.", "_No query yet._"
            result = answer_question(question.strip(), session_id)
            diag_lines = [
                f"**Provider:** {result.provider}",
                f"**Model:** {result.model}",
                f"**Latency:** {result.latency_ms} ms",
                f"**Label:** {result.label}",
                f"**Unverified number flags:** {len(result.flags.get('unverified_numbers', []))}",
            ]
            if result.refusal_reason:
                diag_lines.append(f"**Refusal reason:** {result.refusal_reason}")
            return result.answer, "\n\n".join(diag_lines)

        def on_clear():
            return "", "", "_No query yet._"

        ask_btn.click(on_ask,   inputs=question_box, outputs=[answer_box, diag_box])
        clear_btn.click(on_clear, outputs=[question_box, answer_box, diag_box])

        for btn, q in zip(example_btns, _EXAMPLE_QUERIES):
            btn.click(lambda _q=q: _q, outputs=question_box)
