from typing import Dict, Type

from .base import BaseProvider
from .anthropic import AnthropicProvider
from .openai_provider import OpenAIProvider
from ..exceptions import ProviderError


class ProviderFactory:
    """Factory for creating AI provider instances."""

    _providers: Dict[str, Type[BaseProvider]] = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create(cls, provider_name: str, api_key: str, **kwargs) -> BaseProvider:
        """Create a provider instance."""
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ProviderError(
                f"Unknown provider: {provider_name}. Available providers: {', '.join(cls._providers.keys())}"
            )

        return provider_class(api_key, **kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseProvider]):
        """Register a new provider."""
        cls._providers[name.lower()] = provider_class

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())
