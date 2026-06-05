from typing import AsyncIterator

from openai import AsyncOpenAI

from app.providers.llm import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", embedding_model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = embedding_model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> dict | AsyncIterator[str]:
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        if stream:
            return self._stream(**kwargs)

        resp = await self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        result = {
            "role": "assistant",
            "content": choice.message.content,
        }
        if choice.message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in choice.message.tool_calls
            ]
        return result

    async def _stream(self, **kwargs):
        stream = await self.client.chat.completions.create(**kwargs, stream=True)
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def embed(self, texts: list[str]) -> list[list[float]]:
        resp = await self.client.embeddings.create(
            model=self.embedding_model,
            input=texts,
        )
        return [d.embedding for d in resp.data]

    async def count_tokens(self, text: str) -> int:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": text}],
            max_tokens=1,
        )
        return resp.usage.prompt_tokens if resp.usage else 0
