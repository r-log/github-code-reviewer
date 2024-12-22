from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..models.request import AIRequest
from ..models.response import AIResponse


class AIProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, api_key: str, **kwargs):
        """Initialize provider with API key."""
        self.api_key = api_key
        self.model = kwargs.get("model")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 4000)

    @abstractmethod
    async def generate_review(self, request: AIRequest) -> AIResponse:
        """Generate a code review from the request."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        pass

    @property
    def name(self) -> str:
        """Get provider name."""
        return self.__class__.__name__.lower().replace("provider", "")
