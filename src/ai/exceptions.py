class AIError(Exception):
    """Base exception for AI-related errors."""
    pass


class ProviderError(AIError):
    """Exception raised for errors in the AI provider."""
    pass


class ReviewError(AIError):
    """Exception raised for errors during code review."""
    pass


class ConfigurationError(AIError):
    """Exception raised for configuration-related errors."""
    pass


class TokenLimitError(AIError):
    """Exception raised when token limit is exceeded."""
    pass


class StorageError(AIError):
    """Exception raised for storage-related errors."""
    pass
