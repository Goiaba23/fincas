from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    user_id: str
    workspace_id: str | None = None
    conversation_id: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    data: Any = None
    message: str = ""
    suggestions: list[str] = field(default_factory=list)
    confidence: float = 1.0


class BaseAgent(ABC):
    name: str = "base"
    description: str = "Base agent"
    icon: str = "🤖"
    system_prompt: str = ""
    tools_available: list[str] = field(default_factory=list)

    @abstractmethod
    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        ...

    def get_capabilities(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "tools": self.tools_available,
        }
