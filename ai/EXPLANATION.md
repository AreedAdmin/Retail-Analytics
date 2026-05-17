# AI Module — Design & Explanation

> Target reader: grader, dashboard lead, teammates picking this up for the first time.
> Reading time: ~5 minutes.

---

## 1. What this module does

Module 8 embeds a retail analytics chatbot directly inside the Gradio dashboard. A marketing manager can type plain-English questions and receive answers grounded exclusively in the ML and analytics outputs already visible in the dashboard. Every response is labelled `[Data-grounded]` or `[General inference]` so the manager always knows how much to trust it. The module also provides a "Summarise this chart" click action and a multi-chart synthesis panel used across Modules 3–7.

---

## 2. Why an open-source LLM

We run **Llama 3.1 8B Instruct** via Ollama (local) rather than a proprietary API for four reasons:

1. **Privacy** — on Ollama, no query or response ever leaves the laptop. The dataset stays entirely local.
2. **Cost** — zero per-token cost during development and demo. No surprise bills.
3. **Reproducibility** — the same quantised model weight file produces the same output on every machine. API models can silently change between versions.
4. **Pedagogical transparency** — the team can explain every component end-to-end without a black-box vendor.

If a cloud deployment is needed, a single env-var change (`LLM_PROVIDER=bedrock`) routes the same Llama 3.1 family through **AWS Bedrock** — same model, same prompts, same guardrails, no code changes. That is the "cloud demo story."

---

## 3. Architecture diagram

```
User types question
        │
        ▼
┌─────────────────────────┐
│  Gradio Tab (Module 8)  │  ai/ui/module_8_tab.py
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────┐
│  Input Filter            │  ai/guardrails/input_filter.py
│  (length, PII, injection,│
│   topic gate, raw-data)  │
└──────────┬───────────────┘
           │ allowed?
           ▼
┌──────────────────────────┐
│  Context Builder         │  ai/context/context_builder.py
│  (reads ml/*/outputs/    │  ai/context/context_registry.py
│   ai_context_*.json —    │
│   NEVER data_raw.csv)    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Prompt Template         │  ai/prompts/system_chat.txt
│  str.replace({context})  │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Provider Abstraction    │  ai/providers/__init__.py
│  Ollama ──► local Llama  │  ai/providers/ollama_provider.py
│  Bedrock ► cloud Llama   │  ai/providers/bedrock_provider.py
│  Echo ──► offline stub   │  ai/providers/echo_provider.py
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Output Validator        │  ai/guardrails/output_validator.py
│  (number grounding,      │
│   label enforcement,     │
│   system-leak redaction) │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Logger                  │  ai/logs/interaction_logger.py
│  interactions.jsonl      │
│  interactions.csv        │
└──────────┬───────────────┘
           │
           ▼
  Answer + Diagnostics panel
```

---

## 4. The provider abstraction

| Provider | When used | How to activate |
|---|---|---|
| **Ollama** | Default; Ollama running locally with `llama3.1:8b-instruct-q4_K_M` pulled | `LLM_PROVIDER=ollama` (default) |
| **Bedrock** | AWS deployment; same Llama 3.1 family via `meta.llama3-1-8b-instruct-v1:0` | `LLM_PROVIDER=bedrock` + AWS credentials |
| **Echo** | Offline fallback; deterministic, no network; used by all tests and CI | `LLM_PROVIDER=echo` |

The factory in `ai/providers/__init__.py` calls `health_check()` before returning a real provider. If Ollama is selected but unreachable, it falls back to Echo with a logged warning — the dashboard still loads, the chat just shows offline-mode responses.

---

## 5. Context packaging

**The LLM never sees `data/data_raw.csv`.** It only receives the structured JSON files that the ML pod writes after model training:

| File currently wired | Chart ID | Module |
|---|---|---|
| `ml/ml_promotions_pricing/outputs/ai_context_module7.json` | `module7_lift_summary` | Module 7 — Promotion Lift |

The registry (`ai/context/context_registry.py`) stores a **prioritised candidate list** per chart_id so it can survive ML team renames without code changes (first existing path wins; legacy path kept as fallback).

Future modules (6, 4, 5) have placeholder entries in the registry; they will populate when the ML pod writes their context files.

---

## 6. System prompts

All three prompt templates live in `ai/prompts/`:

| File | Used by | Word cap |
|---|---|---|
| `system_chat.txt` | `chat_service.py` | 2–6 sentences |
| `system_chart_summary.txt` | `chart_summary_service.py` | ≤120 words |
| `system_multi_summary.txt` | `multi_chart_service.py` | ≤200 words |

They live in files, not Python strings, for three reasons:
1. Git history shows prompt changes as diffs, making regressions easy to spot.
2. Non-engineers (e.g., domain experts) can review and edit them without touching code.
3. No f-string interpolation accidents — context is injected via `str.replace("{context_json}", ...)`, matching the pattern established in Module 7.

---

## 7. Guardrails

| Situation | What happens |
|---|---|
| Empty query | refused, `length_too_short`, logged |
| > 1200 chars | refused, `length_too_long`, logged |
| Contains email/phone/card | refused, `pii`, logged |
| Contains "ignore previous instructions" | refused, `prompt_injection`, logged |
| Long off-topic query (no allowlist hits, > 80 chars) | refused, `off_topic`, logged |
| Asks for raw data dump | refused, `raw_data_dump`, logged |
| Ollama unreachable | falls back to `EchoProvider` with a banner in Diagnostics; if Echo also fails (impossible — it's local code), refused as `provider_down` |
| Model output cites a number not in context | label forced to `[General inference]`, `unverified_numbers` populated in log, response still shown |
| Model output echoes system prompt | redacted by `redact_system_leak`, flag set |
| Model output missing label | `[General inference]` appended automatically |

---

## 8. Logging

**`ai/logs/interactions.jsonl`** — one JSON object per event, append-only. See `ai/logs/README.md` for the full schema.

**`ai/logs/interactions.csv`** — rebuilt from the JSONL on every flush. This is the primary input for Module 9 (Critical Reflection) charts.

**Privacy design choice:** By default, the full query text and answer text are NOT stored — only `query_chars` and `answer_chars`. This protects user privacy while still giving Module 9 enough signal for latency, refusal rate, and label distribution analysis. Set `AI_LOG_VERBOSE=1` to store the full text (for local debugging only — never enable in production).

**How to toggle verbose mode:** `export AI_LOG_VERBOSE=1` in the terminal before launching the dashboard.

---

## 9. Doc conflict note

`docs/deliverable.md` states "LLM API — Claude (Anthropic) or OpenAI — API calls only, no local LLMs." The three other authoritative documents — `docs/CLAUDE.md`, `docs/rules.md`, and `docs/tech_stack.md` — all explicitly permit Ollama within the 8 GB RAM cap. We follow the three newer documents: **open-source LLM via Ollama is the primary path**, with AWS Bedrock as an alternative for the same model family. `deliverable.md` has not been updated to reflect this decision; we acknowledge the discrepancy here and note it in `ai/team_logs.md` as a known inconsistency.

---

## 10. Dashboard integration

The dashboard lead needs to add exactly these two lines to `dashboard/app/main.py`:

```python
from dashboard.modules.module_8_chat import build_module_8_chat_tab
# ... inside build_app's main column, after build_module_7_tab():
build_module_8_chat_tab()
```

The first line goes in the import block at the top. The second goes inside the `gr.Blocks` / tab-building section, immediately after the `build_module_7_tab()` call. No other changes are needed.

---

## 11. Known limitations

1. **Number validation is regex-based.** `output_validator.py` matches numbers within 0.5% tolerance using `re.findall` — not a real parser. It will miss numbers expressed as words ("fifty-nine percent") and can over-flag valid rounding (e.g., "approximately 91%" when the context has 91.79).
2. **Off-topic gate is a simple allowlist.** The allowlist in `topic_allowlist.txt` covers ~59 retail analytics terms. Novel valid questions that use none of these terms will pass if they are short (≤80 chars), but be rejected if long. The threshold is a deliberate false-negative trade-off: we accept occasional off-topic pass-throughs rather than blocking valid analytics questions.
3. **No multi-turn memory.** `docs/deliverable.md §8a` is explicit: single-turn Q&A only. Each question is answered independently with no conversation history. This is by design.
4. **Local Llama 3.1 8B vs GPT-4o quality.** Llama 3.1 8B Instruct (Q4 quantised) will occasionally produce weaker summaries than GPT-4o, particularly on complex multi-SKU comparisons. We accept this trade-off for open-source/privacy reasons and will quantify failure cases in Module 9.

---

## 12. How to run it locally

```bash
# 1. Install Ollama (https://ollama.com)
# 2. Pull the model (~4.7 GB download)
ollama pull llama3.1:8b-instruct-q4_K_M

# 3. Install Python deps
pip install -r requirements.txt

# 4. Launch the dashboard (use the entry point defined by the dashboard lead)
LLM_PROVIDER=ollama python -m dashboard.app
```

To run without Ollama (offline/CI mode):
```bash
LLM_PROVIDER=echo python -m dashboard.app
```

To run the test suite (no Ollama required):
```bash
pytest ai/tests/ -v
```
