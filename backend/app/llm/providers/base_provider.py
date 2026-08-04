from abc import abstractmethod
from time import perf_counter

from app.llm.base import BaseLLM
from app.llm.models import LLMRequest, LLMResponse
from loguru import logger


class BaseProvider(BaseLLM):
    """
    Base implementation shared by all LLM providers.

    Child classes only need to implement `_generate()`.
    """

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Standard request lifecycle.
        """

        start = perf_counter()

        logger.info(f"[{self.provider_name}] Generating response using model '{request.model}'")

        try:
            response = await self._generate(request)

            elapsed = round(
                (perf_counter() - start) * 1000,
                2,
            )

            response.metadata["latency_ms"] = elapsed

            logger.info(f"[{self.provider_name}] Completed in {elapsed} ms")

            return response

        except Exception:
            logger.exception(f"[{self.provider_name}] Generation failed")

            raise

    @abstractmethod
    async def _generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Provider-specific implementation.

        Child classes must implement this.
        """
        raise NotImplementedError
