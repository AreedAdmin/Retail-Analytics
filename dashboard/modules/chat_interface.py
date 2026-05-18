"""
Module 8 — AI Chat Interface.
=============================
Three deliverable-required GenAI features, all grounded in real model
outputs and guarded against hallucination by ai/services/guardrail.py:

    8a. Persistent grounded Q&A           (gr.Chatbot)
    8b. Click-to-summarise a module       (one-click summary button)
    8c. Multi-select integrated briefing  (combine modules)

All LLM calls go through ai.services.narrative_service, whose backend is
free by default (open model in-Space) and needs no API key.
"""

from __future__ import annotations

import gradio as gr

from ai.services import narrative_service
from ai.services import context_builder

_SCOPES = context_builder.available_scopes()
_LABELS = context_builder.SCOPE_LABELS
_CHOICES = [(_LABELS.get(s, s), s) for s in _SCOPES]
_SCOPE_DD = [("All modules", "all")] + _CHOICES


def _respond(message: str, history: list, scope: str):
    """Append the user turn + grounded assistant reply (messages format)."""
    history = history or []
    history.append({"role": "user", "content": message})
    reply = narrative_service.chat(message, history, scope=scope)
    history.append({"role": "assistant", "content": reply})
    return history, ""


def build_chat_tab() -> None:
    """Render Module 8 as its own tab (consistent with the other modules)."""
    with gr.Tab("8. AI Assistant"):
        _chat_body()


def _chat_body() -> None:
    gr.Markdown(
        "## 🤖 AI Assistant — Module 8\n"
        "Ask questions about the analytics, or generate one-click summaries. "
        "Every answer is grounded in the model outputs and labelled "
        "**[Data-grounded]** or **[General inference]**."
    )

    with gr.Row():
        # ── 8a: grounded Q&A ────────────────────────────────────────────────
        with gr.Column(scale=3):
            scope = gr.Dropdown(
                choices=_SCOPE_DD,
                value="all",
                label="Grounding scope",
                info="Which module's data the assistant may cite.",
            )
            chatbot = gr.Chatbot(
                label="Retail Analytics Assistant",
                height=420,
            )
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="e.g. Which SKUs respond best to promotions?",
                    scale=8,
                    show_label=False,
                    container=False,
                )
                send = gr.Button("Send", variant="primary", scale=1)
            clear = gr.Button("Clear conversation", size="sm")

        # ── 8b + 8c: summaries ──────────────────────────────────────────────
        with gr.Column(scale=2):
            gr.Markdown("### One-click summary (8b)")
            sum_scope = gr.Dropdown(
                choices=_CHOICES,
                value=_SCOPES[0],
                label="Module to summarise",
            )
            sum_btn = gr.Button("📝 Summarise this module", variant="primary")
            sum_out = gr.Markdown()

            gr.Markdown("### Integrated briefing (8c)")
            multi = gr.CheckboxGroup(
                choices=_CHOICES,
                value=_SCOPES,
                label="Combine modules",
            )
            multi_btn = gr.Button("🧩 Generate integrated briefing")
            multi_out = gr.Markdown()

    gr.Markdown(
        f"<sub>LLM backend: **{narrative_service.backend_label()}** · "
        "responses post-processed by the grounding guardrail.</sub>"
    )

    # ── wiring ──────────────────────────────────────────────────────────────
    send.click(_respond, [msg, chatbot, scope], [chatbot, msg])
    msg.submit(_respond, [msg, chatbot, scope], [chatbot, msg])
    clear.click(lambda: ([], ""), None, [chatbot, msg])

    sum_btn.click(narrative_service.summarise_scope, [sum_scope], [sum_out])
    multi_btn.click(narrative_service.multi_summary, [multi], [multi_out])
