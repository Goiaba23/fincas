from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.providers.llm import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> dict | AsyncIterator[str]:
        system = None
        msgs = messages
        if messages and messages[0].get("role") == "system":
            system = messages[0]["content"]
            msgs = messages[1:]

        kwargs = dict(
            model=self.model,
            messages=msgs,
            max_tokens=4096,
        )
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = [
                {"name": t["function"]["name"], "description": t["function"].get("description", ""),
                 "input_schema": t["function"].get("parameters", {})}
                for t in tools
            ]

        if stream:
            return self._stream(**kwargs)

        resp = await self.client.messages.create(**kwargs)
        content = ""
        tool_calls = []
        for block in resp.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {"name": block.name, "arguments": str(block.input)},
                })

        return {"role": "assistant", "content": content or None, "tool_calls": tool_calls or None}

    async def _stream(self, **kwargs):
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("Anthropic does not provide embedding API")

    async def count_tokens(self, text: str) -> int:
        return await self.client.count_tokens(text)
