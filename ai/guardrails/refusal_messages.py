# AI-assisted: reviewed by [name]
"""Canned refusal copy keyed by reason code."""

REFUSALS: dict[str, str] = {
    "length_too_short": "Your question is too short — please rephrase with more detail.",
    "length_too_long":  "Your question is too long ({n} chars, max {max}). Please shorten it.",
    "pii":              "I can't process messages containing personal information.",
    "prompt_injection": "I can't follow instructions to change my behaviour. Ask a retail analytics question instead.",
    "off_topic":        "I'm scoped to this dashboard's retail analytics outputs. Try asking about SKUs, demand, promotions, pricing, or scenarios.",
    "raw_data_dump":    "I don't expose the raw dataset. I can summarise model outputs — for example, lift % by SKU or scenario revenue impact.",
    "provider_down":    "The AI model is unreachable right now. Model outputs in the dashboard are still valid; only the chat is unavailable.",
}


def get_refusal(reason: str, **kwargs) -> str:
    """Return the refusal string for reason, with optional format kwargs."""
    msg = REFUSALS.get(reason, "I can't help with that request.")
    try:
        return msg.format(**kwargs)
    except KeyError:
        return msg
