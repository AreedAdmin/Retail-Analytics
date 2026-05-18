# AI-assisted: reviewed by [name]
"""
tail_logs — pretty-print recent entries from interactions.jsonl.

Usage: python ai/scripts/tail_logs.py [N]   (default: last 10 entries)
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ai.config.settings import INTERACTIONS_JSONL

n = int(sys.argv[1]) if len(sys.argv) > 1 else 10

if not INTERACTIONS_JSONL.exists():
    print("No interactions log found yet. Run a query first.")
    sys.exit(0)

lines = INTERACTIONS_JSONL.read_text(encoding="utf-8").strip().splitlines()
recent = lines[-n:]

print(f"\n{'='*60}")
print(f"Last {len(recent)} entries from {INTERACTIONS_JSONL.name}")
print(f"{'='*60}\n")

for raw in recent:
    try:
        e = json.loads(raw)
        print(
            f"[{e.get('timestamp_utc','?')}] "
            f"{e.get('event_type','?'):15s} "
            f"provider={e.get('provider','?'):8s} "
            f"label={e.get('answer_label','?'):20s} "
            f"latency={e.get('latency_ms','?')}ms "
            f"refusal={e.get('refusal_reason') or '-'}"
        )
    except json.JSONDecodeError:
        print(f"  [malformed line] {raw[:80]}")
