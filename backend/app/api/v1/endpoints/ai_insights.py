from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.insights.engine import run_all_agents, calculate_health_score

router = APIRouter(prefix="/ai/insights", tags=["ai"])


@router.get("/dashboard")
async def dashboard_insights(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    results = await run_all_agents(db, str(user.id))
    health = calculate_health_score(results)

    # Collect all suggestions and top messages
    all_suggestions = []
    for agent_name, agent_result in results.items():
        if agent_result.get("success") and agent_result.get("suggestions"):
            all_suggestions.extend(
                {"agent": agent_name, "icon": agent_result.get("icon", "🤖"), "text": s}
                for s in agent_result["suggestions"]
            )

    all_suggestions.sort(key=lambda x: 0 if any(k in x["text"] for k in ["🔴", "⚠️", "🔥", "⏰"]) else 1)

    return {
        "health_score": health,
        "agents": results,
        "insights": all_suggestions[:10],
    }


@router.get("/health-score")
async def health_score(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    results = await run_all_agents(db, str(user.id))
    return calculate_health_score(results)


@router.get("/suggestions")
async def suggestions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    results = await run_all_agents(db, str(user.id))
    all_suggestions = []
    for agent_name, agent_result in results.items():
        if agent_result.get("success") and agent_result.get("suggestions"):
            all_suggestions.extend(
                {"agent": agent_name, "icon": agent_result.get("icon", "🤖"), "text": s}
                for s in agent_result["suggestions"]
            )
    return {"suggestions": all_suggestions[:10]}
