from abc import ABC, abstractmethod
from typing import AsyncIterator


class ToolCall:
    name: str
    arguments: dict


class LLMMessage:
    role: str  # system, user, assistant, tool
    content: str | None
    tool_calls: list[ToolCall] | None
    tool_call_id: str | None


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> dict | AsyncIterator[str]:
        ...

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        ...
