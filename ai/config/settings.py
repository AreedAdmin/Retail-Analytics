# AI-assisted: reviewed by [name]
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_ROOT = REPO_ROOT / "ai"

# ── Provider routing ─────────────────────────────────────────────
# Values: "ollama", "bedrock", "echo"
# Echo is the deterministic fallback used when no LLM is reachable.
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()

# ── Open-source model identifier ─────────────────────────────────
# Default model is small enough for the 8 GB RAM cap (rules.md §7).
# Ollama tag: llama3.1:8b-instruct-q4_K_M  (~4.7 GB resident)
# Bedrock id:  meta.llama3-1-8b-instruct-v1:0
OLLAMA_MODEL  = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")
OLLAMA_HOST   = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
BEDROCK_MODEL = os.environ.get("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
BEDROCK_REGION = os.environ.get("AWS_REGION", "eu-west-2")

# ── Generation limits ────────────────────────────────────────────
MAX_INPUT_CHARS   = 1200          # rejected above this
MAX_OUTPUT_TOKENS = 512
TEMPERATURE       = 0.2           # deliberately low — analytics, not creative
TIMEOUT_SECONDS   = 30

# ── Guardrails ───────────────────────────────────────────────────
MIN_QUERY_CHARS   = 3
MAX_NUMBERS_UNVERIFIED = 0        # any unverified number → flag as [General inference]

# ── Paths ────────────────────────────────────────────────────────
PROMPTS_DIR        = AI_ROOT / "prompts"
LOGS_DIR           = AI_ROOT / "logs"
INTERACTIONS_JSONL = LOGS_DIR / "interactions.jsonl"
INTERACTIONS_CSV   = LOGS_DIR / "interactions.csv"
TOPIC_ALLOWLIST    = AI_ROOT / "config" / "topic_allowlist.txt"
