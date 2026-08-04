"""Groq LPU HTTPX REST Provider."""

import httpx
from app.core.settings import settings
from app.llm.base import BaseLLM
from app.llm.models import LLMProvider, LLMRequest, LLMResponse, TokenUsage


class GroqLLM(BaseLLM):
    """Groq LPU Provider."""

    @property
    def provider_name(self) -> str:
        return LLMProvider.GROQ.value

    @property
    def supports_streaming(self) -> bool:
        return False

    async def generate(self, request: LLMRequest) -> LLMResponse:
        api_key = settings.GROQ_API_KEY.get_secret_value()
        model_name = request.model if request.model and "/" not in request.model else "llama-3.3-70b-versatile"

        messages = [{"role": m.role.value, "content": m.content} for m in request.messages]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or 2048,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return LLMResponse(
                provider=self.provider_name,
                model=model_name,
                content=content,
                usage=TokenUsage(prompt_tokens=100, completion_tokens=500, total_tokens=600),
            )
