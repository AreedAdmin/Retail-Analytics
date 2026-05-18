# AI-assisted: reviewed by [name]
"""
Environment + wiring smoke check for the AI module.

Run with: python ai/scripts/check_setup.py
Exits 0 if all HARD checks pass; 1 otherwise.
WARN items do not affect the exit code.
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

_HARD_FAILS: list[str] = []
_WARNS: list[str] = []
_OKS: list[str] = []


def ok(msg: str) -> None:
    _OKS.append(msg)
    print(f"  [OK]   {msg}")


def warn(msg: str) -> None:
    _WARNS.append(msg)
    print(f"  [WARN] {msg}")


def fail(msg: str) -> None:
    _HARD_FAILS.append(msg)
    print(f"  [FAIL] {msg}")


# ── Check 1: Python version ──────────────────────────────────────────────────

print("\n1. Python version")
major, minor = sys.version_info.major, sys.version_info.minor
if (major, minor) >= (3, 11):
    ok(f"Python {major}.{minor} >= 3.11")
else:
    fail(f"Python {major}.{minor} < 3.11 — upgrade required")

# ── Check 2: Required packages ───────────────────────────────────────────────

print("\n2. Required packages")
for pkg in ["ollama", "boto3", "requests", "anthropic"]:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", pkg],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        version_line = next(
            (l for l in result.stdout.splitlines() if l.startswith("Version:")),
            "Version: unknown"
        )
        ok(f"{pkg} installed ({version_line})")
    else:
        fail(f"{pkg} not installed — run: pip install -r requirements.txt")

# ── Check 3: Required files ──────────────────────────────────────────────────

print("\n3. Required files")
from ai.config.settings import (
    PROMPTS_DIR, LOGS_DIR, INTERACTIONS_JSONL, INTERACTIONS_CSV, TOPIC_ALLOWLIST,
    AI_ROOT
)

required_paths: list[Path] = [
    AI_ROOT / "__init__.py",
    AI_ROOT / "config" / "settings.py",
    AI_ROOT / "config" / "topic_allowlist.txt",
    PROMPTS_DIR / "system_chat.txt",
    PROMPTS_DIR / "system_chart_summary.txt",
    PROMPTS_DIR / "system_multi_summary.txt",
    PROMPTS_DIR / "module7_lift_narrative.txt",
    LOGS_DIR,
    TOPIC_ALLOWLIST,
]
for p in required_paths:
    if p.exists():
        ok(str(p.relative_to(REPO_ROOT)))
    else:
        fail(f"Missing: {p.relative_to(REPO_ROOT)}")

# ── Check 4: data/data_raw.csv ───────────────────────────────────────────────

print("\n4. data/data_raw.csv")
raw_csv = REPO_ROOT / "data" / "data_raw.csv"
if raw_csv.exists():
    with open(raw_csv, encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1  # subtract header
    if row_count > 4000:
        ok(f"data_raw.csv exists with {row_count:,} rows")
    else:
        fail(f"data_raw.csv has only {row_count} rows (expected > 4000)")
else:
    fail("data/data_raw.csv not found")

# ── Check 5: ML context file ─────────────────────────────────────────────────

print("\n5. ML context file")
from ai.context.context_registry import resolve_context_path
ctx_path = resolve_context_path("module7_lift_summary")
if ctx_path and ctx_path.exists():
    ok(f"ai_context_module7.json found at {ctx_path.relative_to(REPO_ROOT)}")
else:
    fail("ai_context_module7.json not found in any candidate path")

# ── Check 6: topic_allowlist.txt ─────────────────────────────────────────────

print("\n6. topic_allowlist.txt")
if TOPIC_ALLOWLIST.exists():
    lines = [l for l in TOPIC_ALLOWLIST.read_text().splitlines() if l.strip()]
    if len(lines) >= 30:
        ok(f"topic_allowlist.txt has {len(lines)} terms (>= 30)")
    else:
        fail(f"topic_allowlist.txt has only {len(lines)} terms (need >= 30)")
else:
    fail("topic_allowlist.txt not found")

# ── Check 7: Ollama health check ─────────────────────────────────────────────

print("\n7. Ollama health check")
try:
    from ai.providers.ollama_provider import OllamaProvider
    p = OllamaProvider()
    if p.health_check():
        ok("Ollama reachable · model available")
    else:
        warn("Ollama not reachable or model not pulled — will use EchoProvider")
except Exception as exc:
    warn(f"Ollama check error: {exc} — will use EchoProvider")

# ── Check 8: boto3 credentials ───────────────────────────────────────────────

print("\n8. boto3 / AWS credentials")
try:
    import boto3
    session = boto3.Session()
    creds = session.get_credentials()
    if creds is not None:
        ok("boto3 credentials resolvable")
    else:
        warn("boto3 installed but no AWS credentials found — Bedrock unavailable")
except ImportError:
    warn("boto3 not installed — Bedrock provider unavailable")
except Exception as exc:
    warn(f"boto3 credentials check error: {exc}")

# ── Check 9: End-to-end EchoProvider smoke test ──────────────────────────────

print("\n9. End-to-end EchoProvider smoke test")
os.environ["LLM_PROVIDER"] = "echo"
try:
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tf:
        tmp_log = Path(tf.name)

    from ai.context.context_builder import build_chat_context
    from ai.config.settings import PROMPTS_DIR
    from ai.providers.echo_provider import EchoProvider
    from ai.guardrails.output_validator import validate_output
    from ai.logs.interaction_logger import log_interaction

    ctx = build_chat_context()
    ctx_json = json.dumps(ctx, indent=2)
    template = (PROMPTS_DIR / "system_chat.txt").read_text(encoding="utf-8")
    system_prompt = template.replace("{context_json}", ctx_json)

    provider = EchoProvider()
    resp = provider.generate(system_prompt, "What is the median lift?")
    clean, flags = validate_output(resp.text, ctx)

    has_label = "[General inference]" in clean or "[Data-grounded]" in clean
    if not has_label:
        fail("E2E smoke: response missing label")
    else:
        log_interaction(
            session_id="check00", event_type="chat_query",
            user_query="What is the median lift?",
            context_modules=[k for k in ctx if k != "_missing"],
            provider="echo", model="echo-v1",
            system_prompt_id="system_chat_v1",
            latency_ms=0, tokens_in=None, tokens_out=None,
            answer_label="General inference",
            answer_text=clean,
            guardrail_input={"allowed": True, "reason": None},
            guardrail_output=flags,
            log_path=tmp_log,
        )
        ok("E2E smoke passed — labelled response written to temp log")
        tmp_log.unlink(missing_ok=True)
        tmp_log.with_suffix(".csv").unlink(missing_ok=True)

except Exception as exc:
    fail(f"E2E smoke test error: {exc}")

# ── Summary ──────────────────────────────────────────────────────────────────

print()
print("=" * 50)
if _WARNS:
    for w in _WARNS:
        print(f"  WARN: {w}")
print()
if _HARD_FAILS:
    for f in _HARD_FAILS:
        print(f"  FAIL: {f}")
    print(f"\nResult: FAIL ({len(_HARD_FAILS)} hard check(s) failed, {len(_WARNS)} warning(s))")
    sys.exit(1)
else:
    print(f"Result: OK ({len(_OKS)} checks passed, {len(_WARNS)} warning(s))")
    sys.exit(0)
