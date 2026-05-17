# AI-assisted: reviewed by [name]
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class LlmProviderError(Exception):
    """Raised when a provider fails to generate a response."""


@dataclass
class LlmResponse:
    text: str
    model: str
    provider: str
    latency_ms: int
    tokens_in: int | None        # provider may not return this
    tokens_out: int | None
    raw: dict = field(default_factory=dict)  # full provider payload, for the log


class LlmProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> LlmResponse: ...

    def health_check(self) -> bool:
        return False
