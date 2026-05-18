# AI-assisted: reviewed by [name]
"""
Provider factory.

Reads LLM_PROVIDER from settings and returns the appropriate
LlmProvider instance. Falls back to EchoProvider with a logged
warning if the selected provider's health_check() is False.
"""
import logging

from ai.config.settings import LLM_PROVIDER
from .base import LlmProvider
from .echo_provider import EchoProvider

logger = logging.getLogger(__name__)


def get_provider() -> LlmProvider:
    provider_name = LLM_PROVIDER

    if provider_name == "echo":
        return EchoProvider()

    if provider_name == "ollama":
        from .ollama_provider import OllamaProvider
        p = OllamaProvider()
        if p.health_check():
            return p
        logger.warning(
            "Ollama health check failed (model not reachable). "
            "Falling back to EchoProvider."
        )
        return EchoProvider()

    if provider_name == "bedrock":
        from .bedrock_provider import BedrockProvider
        p = BedrockProvider()
        if p.health_check():
            return p
        logger.warning(
            "Bedrock health check failed (credentials or client error). "
            "Falling back to EchoProvider."
        )
        return EchoProvider()

    logger.warning(
        "Unknown LLM_PROVIDER=%r. Falling back to EchoProvider.", provider_name
    )
    return EchoProvider()
