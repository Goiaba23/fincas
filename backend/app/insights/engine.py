from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import get_all_agents, register_agent
from app.agents.base import AgentContext


async def run_all_agents(db: AsyncSession, user_id: str, workspace_id: str | None = None) -> dict:
    context = AgentContext(user_id=user_id, workspace_id=workspace_id)
    results = {}

    for agent in get_all_agents():
        try:
            result = await agent.run(context, db=db)
            results[agent.name] = {
                "name": agent.name,
                "description": agent.description,
                "icon": agent.icon,
                "success": result.success,
                "data": result.data,
                "message": result.message,
                "suggestions": result.suggestions,
            }
        except Exception as e:
            results[agent.name] = {
                "name": agent.name,
                "error": str(e),
                "success": False,
            }

    return results


def calculate_health_score(agent_results: dict) -> dict:
    score = 100
    breakdown = {}

    if spending := agent_results.get("analista_gastos", {}).get("data"):
        change = spending.get("change_pct", 0)
        if change > 20:
            score -= 15
            breakdown["gastos"] = -15
        elif change > 10:
            score -= 5
            breakdown["gastos"] = -5
        else:
            breakdown["gastos"] = 5

    if budget := agent_results.get("analista_orcamentos", {}).get("data"):
        budgets = budget.get("budgets", [])
        if budgets:
            over_budget = sum(1 for b in budgets if b.get("percentage", 0) > 100)
            score -= over_budget * 10
            breakdown["orcamentos"] = -over_budget * 10
        else:
            score -= 10
            breakdown["orcamentos"] = -10

    if debt := agent_results.get("consultor_dividas", {}).get("data"):
        total_debt = debt.get("total_debt", 0)
        income = debt.get("monthly_income", 0)
        if total_debt > 0:
            ratio = (total_debt / max(income, 1)) * 100
            if ratio > 50:
                score -= 25
                breakdown["dividas"] = -25
            elif ratio > 30:
                score -= 10
                breakdown["dividas"] = -10
            else:
                breakdown["dividas"] = 0
        else:
            breakdown["dividas"] = 10

    if goal_data := agent_results.get("analista_metas", {}).get("data"):
        goals = goal_data.get("goals", [])
        if goals:
            avg_pct = sum(g.get("percentage", 0) for g in goals) / len(goals)
            if avg_pct > 75:
                breakdown["metas"] = 10
            elif avg_pct > 50:
                breakdown["metas"] = 5
            else:
                breakdown["metas"] = 0
        else:
            score -= 5
            breakdown["metas"] = -5

    if subs := agent_results.get("detetive_assinaturas", {}).get("data"):
        count = subs.get("count", 0)
        total = subs.get("total_monthly", 0)
        if count > 5:
            score -= max(10, count * 2)
            breakdown["assinaturas"] = -min(20, count * 2)
        elif count > 3:
            breakdown["assinaturas"] = -5
        else:
            breakdown["assinaturas"] = 5

    score = max(0, min(100, score))
    return {
        "score": score,
        "level": _health_level(score),
        "breakdown": breakdown,
    }


def _health_level(score: int) -> str:
    if score >= 80: return "excelente"
    if score >= 60: return "boa"
    if score >= 40: return "atencao"
    if score >= 20: return "critica"
    return "emergencia"
