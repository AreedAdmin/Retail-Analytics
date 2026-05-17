# AI-assisted: reviewed by [name]
"""
Append-only interaction logger.

Writes one JSON line per event to interactions.jsonl and rebuilds
interactions.csv on every flush.  Privacy: full query/answer text is
only stored when AI_LOG_VERBOSE=1.
"""
import csv
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ai.config.settings import INTERACTIONS_JSONL, INTERACTIONS_CSV, LOGS_DIR

_VERBOSE = os.environ.get("AI_LOG_VERBOSE", "0") == "1"

_CSV_COLUMNS = [
    "event_id", "timestamp_utc", "session_id", "event_type",
    "provider", "model", "latency_ms", "tokens_in", "tokens_out",
    "answer_label", "unverified_numbers_count", "refusal_reason",
    "query_chars", "answer_chars",
]


def _ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_interaction(
    *,
    session_id: str,
    event_type: str,
    user_query: str,
    context_modules: list[str],
    provider: str,
    model: str,
    system_prompt_id: str,
    latency_ms: int,
    tokens_in: int | None,
    tokens_out: int | None,
    answer_label: str,
    answer_text: str,
    guardrail_input: dict,
    guardrail_output: dict,
    refusal_reason: str | None = None,
    error: str | None = None,
    log_path: Path | None = None,
) -> str:
    """
    Append one event to interactions.jsonl and rebuild interactions.csv.
    Returns the event_id.
    """
    _ensure_logs_dir()
    event_id = uuid.uuid4().hex
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
         f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"

    record = {
        "event_id":          event_id,
        "timestamp_utc":     ts,
        "session_id":        session_id,
        "event_type":        event_type,
        "user_query":        user_query[:500] if _VERBOSE else "",
        "query_chars":       len(user_query),
        "context_modules":   context_modules,
        "provider":          provider,
        "model":             model,
        "system_prompt_id":  system_prompt_id,
        "latency_ms":        latency_ms,
        "tokens_in":         tokens_in,
        "tokens_out":        tokens_out,
        "answer_label":      answer_label,
        "answer_chars":      len(answer_text),
        "guardrail_input":   guardrail_input,
        "guardrail_output":  guardrail_output,
        "refusal_reason":    refusal_reason,
        "error":             error,
    }

    target = log_path or INTERACTIONS_JSONL
    with open(target, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    _rebuild_csv(target, log_path)
    return event_id


def _rebuild_csv(jsonl_path: Path, log_path: Path | None = None) -> None:
    """Rebuild the CSV from the full JSONL file."""
    csv_path = log_path.with_suffix(".csv") if log_path else INTERACTIONS_CSV
    rows: list[dict] = []
    try:
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    rows.append({
                        "event_id":                obj.get("event_id", ""),
                        "timestamp_utc":           obj.get("timestamp_utc", ""),
                        "session_id":              obj.get("session_id", ""),
                        "event_type":              obj.get("event_type", ""),
                        "provider":                obj.get("provider", ""),
                        "model":                   obj.get("model", ""),
                        "latency_ms":              obj.get("latency_ms", ""),
                        "tokens_in":               obj.get("tokens_in", ""),
                        "tokens_out":              obj.get("tokens_out", ""),
                        "answer_label":            obj.get("answer_label", ""),
                        "unverified_numbers_count": len(
                            obj.get("guardrail_output", {}).get("unverified_numbers", [])
                        ),
                        "refusal_reason":          obj.get("refusal_reason", ""),
                        "query_chars":             obj.get("query_chars", ""),
                        "answer_chars":            obj.get("answer_chars", ""),
                    })
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        return

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
