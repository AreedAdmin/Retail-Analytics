# AI Interaction Logs

Two files are written at runtime inside this directory:

---

## interactions.jsonl

Append-only, one JSON object per line. Created on first write.

### Schema (fields in order)

| Field | Type | Description |
|---|---|---|
| `event_id` | string | UUID hex (32 chars) |
| `timestamp_utc` | string | ISO-8601 UTC, e.g. `2026-05-17T12:34:56.789Z` |
| `session_id` | string | 8-char hex, one per page-load |
| `event_type` | string | `chat_query`, `chart_summary`, `multi_summary`, `refusal`, `error` |
| `user_query` | string | Query text, truncated to 500 chars (full text only if `AI_LOG_VERBOSE=1`) |
| `query_chars` | int | Length of the original query |
| `context_modules` | list[str] | Module names loaded into context |
| `provider` | string | `ollama`, `bedrock`, or `echo` |
| `model` | string | Model identifier, e.g. `llama3.1:8b-instruct-q4_K_M` |
| `system_prompt_id` | string | Prompt file stem, e.g. `system_chat_v1` |
| `latency_ms` | int | End-to-end LLM latency |
| `tokens_in` | int or null | Input tokens (if provider reports them) |
| `tokens_out` | int or null | Output tokens (if provider reports them) |
| `answer_label` | string | `Data-grounded`, `General inference`, or `n/a` |
| `answer_chars` | int | Length of the final answer |
| `guardrail_input` | object | `{allowed, reason}` from input filter |
| `guardrail_output` | object | `{unverified_numbers, label_auto_added, system_leak_redacted}` |
| `refusal_reason` | string or null | Reason code if refused, else null |
| `error` | string or null | Exception message if an error occurred |

**Privacy note:** By default, only `query_chars` and `answer_chars` are stored,
not the full query or answer text. Set `AI_LOG_VERBOSE=1` to store full text.

---

## interactions.csv

Rebuilt from `interactions.jsonl` on every flush. Flat subset of the JSON.

### Columns

`event_id, timestamp_utc, session_id, event_type, provider, model,
latency_ms, tokens_in, tokens_out, answer_label, unverified_numbers_count,
refusal_reason, query_chars, answer_chars`

This CSV is the primary input for Module 9 (Critical Reflection) charts:
provider reliability, latency distribution, refusal rates, label breakdown.
