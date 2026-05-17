
"""
Module 7 — AI Narrative Service
================================
Loads the prompt template from ai/prompts/module7_lift_narrative.txt,
injects the context payload from the ML model, calls the Anthropic API,
and returns a labelled response string for the dashboard to render.

Called by: dashboard/modules/module_7.py
Prompt template: ai/prompts/module7_lift_narrative.txt
Context source: ml/promotions/outputs/ai_context_module7.json
"""

import os
import json
import anthropic
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

REPO_ROOT     = Path(__file__).resolve().parents[2]
PROMPT_PATH   = REPO_ROOT / "ai" / "prompts" / "module7_lift_narrative.txt"
CONTEXT_PATH  = REPO_ROOT / "ml" / "ml_promotions_pricing" / "outputs" / "ai_context_module7.json"
FAILURE_LOG   = REPO_ROOT / "ai" / "services" / "failure_log.jsonl"

# ── API setup ─────────────────────────────────────────────────────────────────
# API key is stored as a GitHub Repository Secret — never hardcoded here
# Locally: export ANTHROPIC_API_KEY=your_key in terminal before running

def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found. "
            "Set it as a GitHub Repository Secret or export it in your terminal."
        )
    return anthropic.Anthropic(api_key=api_key)


# ── Prompt loader ─────────────────────────────────────────────────────────────

def load_prompt_template() -> str:
    """Load prompt from file — never inline strings per project rules."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt template not found: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


# ── Context loader ────────────────────────────────────────────────────────────

def load_context(context_override: dict = None) -> dict:
    """
    Load AI context payload.
    Accepts an override dict so the dashboard can pass
    freshly-computed context without reading from disk.
    """
    if context_override:
        return context_override
    if not CONTEXT_PATH.exists():
        raise FileNotFoundError(f"Context file not found: {CONTEXT_PATH}")
    with open(CONTEXT_PATH, "r") as f:
        return json.load(f)


# ── Response validator ────────────────────────────────────────────────────────

def validate_response(response_text: str, context: dict) -> list[str]:
    """
    Basic guardrail: check that numbers in the response
    actually appear in the context payload.
    Returns a list of warnings (empty = clean).
    """
    warnings = []
    context_str = json.dumps(context)

    import re
    numbers_in_response = re.findall(r"\b\d+\.?\d*\b", response_text)

    for num in numbers_in_response:
        if num not in context_str:
            warnings.append(f"Possible hallucination: '{num}' not found in context")

    return warnings


# ── Failure logger ────────────────────────────────────────────────────────────

def log_failure(prompt: str, response: str, warnings: list[str]) -> None:
    """
    Log bad AI outputs for Module 9 (Critical Reflection).
    Appends one JSON line per failure to failure_log.jsonl
    """
    FAILURE_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "module"  : "module_7",
        "prompt_excerpt": prompt[:200],
        "response_excerpt": response[:300],
        "warnings": warnings,
    }
    with open(FAILURE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── Main function ─────────────────────────────────────────────────────────────

def generate_lift_narrative(context_override: dict = None) -> str:
    """
    Main entry point called by the Gradio dashboard.

    Returns a string containing:
    - The AI-generated narrative (150-200 words)
    - A [Data-grounded] or [General inference] label at the end

    If the API call fails, returns a safe fallback message
    so the dashboard never crashes.
    """
    try:
        # 1. Load template and context
        template = load_prompt_template()
        context  = load_context(context_override)

        # 2. Inject context into prompt
        prompt = template.replace("{context_json}", json.dumps(context, indent=2))

        # 3. Call Anthropic API
        client   = get_client()
        message  = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 600,
            messages   = [{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text.strip()

        # 4. Validate response against context (guardrail)
        warnings = validate_response(response_text, context)

        # 5. Log failures for Module 9
        if warnings:
            log_failure(prompt, response_text, warnings)

        return response_text

    except EnvironmentError as e:
        # API key missing — surface clearly in dashboard
        return (
            f"⚠️ API key not configured: {e}\n\n"
            "[General inference]"
        )

    except Exception as e:
        # Any other error — return safe fallback, never crash dashboard
        return (
            f"⚠️ AI narrative unavailable: {str(e)}\n\n"
            "The model outputs are still valid — only the AI summary could not be generated.\n\n"
            "[General inference]"
        )


# ── Click-to-summarise (Module 8b) ───────────────────────────────────────────

def summarise_chart(chart_id: str, chart_data: dict) -> str:
    """
    Called when user clicks 'Summarise this chart' on any Module 7 chart.
    Packages only that chart's data as context and calls the API.
    """
    chart_context = {
        "module_name": "module_7_promotion_lift",
        "chart_id"   : chart_id,
        "chart_data" : chart_data,
    }

    prompt = f"""You are a retail analytics assistant.
Summarise the following chart data in 2-3 plain English sentences for a marketing manager.
Only reference figures present in the data below.
End with [Data-grounded] or [General inference].

Chart: {chart_id}
Data: {json.dumps(chart_context, indent=2)}
"""

    try:
        client  = get_client()
        message = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 200,
            messages   = [{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()

    except Exception as e:
        return f"⚠️ Summary unavailable: {str(e)}\n[General inference]"


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing generate_lift_narrative() ...")
    result = generate_lift_narrative()
    print(result)
