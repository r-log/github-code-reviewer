from typing import Dict, Type

from .base import AIProvider
from .anthropic import AnthropicProvider


class ProviderFactory:
    """Factory for creating AI providers."""

    _providers: Dict[str, Type[AIProvider]] = {
        'anthropic': AnthropicProvider,
    }

    @classmethod
    def create(cls, provider_name: str, **kwargs) -> AIProvider:
        """Create an AI provider instance."""
        if provider_name not in cls._providers:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {', '.join(cls._providers.keys())}"
            )

        return cls._providers[provider_name](**kwargs)

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names."""
        return list(cls._providers.keys())
