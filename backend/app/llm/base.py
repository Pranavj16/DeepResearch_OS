from abc import ABC, abstractmethod

from app.llm.models import LLMRequest, LLMResponse


class BaseLLM(ABC):
    """
    Abstract base class for all LLM providers.

    Every provider implementation must inherit from this class
    and implement all abstract methods.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the provider name.

        Example:
            "gemini"
            "nvidia"
            "groq"
            "openrouter"
        """
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Parameters
        ----------
        request : LLMRequest

        Returns
        -------
        LLMResponse
        """
        raise NotImplementedError

    async def health_check(self) -> bool:
        """
        Optional provider health check.

        Providers can override this method.
        """

        return True
