from app.agents.base import BaseAgent
from app.agents.spending import SpendingAnalystAgent
from app.agents.budget import BudgetAgent
from app.agents.goal import GoalAgent
from app.agents.debt import DebtAgent
from app.agents.subscription import SubscriptionDetectiveAgent

_agents: dict[str, BaseAgent] = {}


def register_agent(agent: BaseAgent):
    _agents[agent.name] = agent


def get_agent(name: str) -> BaseAgent | None:
    return _agents.get(name)


def get_all_agents() -> list[BaseAgent]:
    return list(_agents.values())


def get_capabilities() -> list[dict]:
    return [a.get_capabilities() for a in _agents.values()]


# Register all agents
register_agent(SpendingAnalystAgent())
register_agent(BudgetAgent())
register_agent(GoalAgent())
register_agent(DebtAgent())
register_agent(SubscriptionDetectiveAgent())
