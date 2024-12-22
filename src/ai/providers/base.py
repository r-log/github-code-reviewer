from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..models.request import AIRequest
from ..models.response import AIResponse


class BaseProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate_review(self, request: AIRequest) -> AIResponse:
        """Generate a code review response."""
        pass

    @abstractmethod
    async def validate_configuration(self) -> bool:
        """Validate the provider configuration."""
        pass

    @abstractmethod
    def get_token_limit(self) -> int:
        """Get the maximum token limit for the model."""
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the given text."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name."""
        pass
