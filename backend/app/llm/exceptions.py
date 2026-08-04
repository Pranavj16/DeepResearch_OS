"""
LLM Exception Definitions.

All provider-specific errors should be converted into one of these
exceptions before propagating to the rest of the application.
"""


class LLMException(Exception):
    """Base exception for all LLM-related errors."""


class ProviderNotFoundError(LLMException):
    """Raised when a requested provider is not registered."""


class ProviderAuthenticationError(LLMException):
    """Raised when authentication with an LLM provider fails."""


class ProviderRateLimitError(LLMException):
    """Raised when the provider rate limit is exceeded."""


class ProviderTimeoutError(LLMException):
    """Raised when a provider request times out."""


class ProviderConnectionError(LLMException):
    """Raised when the provider cannot be reached."""


class InvalidResponseError(LLMException):
    """Raised when the provider returns an invalid response."""


class UnsupportedModelError(LLMException):
    """Raised when a model is unsupported by a provider."""
