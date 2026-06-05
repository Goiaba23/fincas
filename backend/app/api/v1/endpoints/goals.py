from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.goal import Goal

router = APIRouter(prefix="/goals", tags=["goals"])


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: date | None = None
    account_id: str | None = None
    category_id: str | None = None
    description: str | None = None


class GoalUpdate(BaseModel):
    current_amount: float | None = None
    is_completed: bool | None = None


@router.get("/")
async def list_goals(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Goal)
        .where(Goal.is_completed == False)
        .order_by(Goal.sort_order)
    )
    goals = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "name": g.name,
            "target": float(g.target_amount),
            "current": float(g.current_amount),
            "progress": round(float(g.current_amount) / float(g.target_amount) * 100, 1) if g.target_amount > 0 else 0,
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "description": g.description,
        }
        for g in goals
    ]


@router.post("/", status_code=201)
async def create_goal(
    req: GoalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    goal = Goal(
        name=req.name,
        target_amount=req.target_amount,
        target_date=req.target_date,
        account_id=req.account_id,
        category_id=req.category_id,
        description=req.description,
    )
    db.add(goal)
    return {
        "id": str(goal.id),
        "name": goal.name,
        "target": float(goal.target_amount),
        "progress": 0,
    }


@router.patch("/{goal_id}")
async def update_goal(
    goal_id: UUID,
    req: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Goal).where(Goal.id == goal_id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(404)

    if req.current_amount is not None:
        goal.current_amount = req.current_amount
    if req.is_completed:
        goal.is_completed = True

    return {
        "id": str(goal.id),
        "current": float(goal.current_amount),
        "progress": round(float(goal.current_amount) / float(goal.target_amount) * 100, 1) if goal.target_amount > 0 else 0,
    }


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Goal).where(Goal.id == goal_id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(404)
    await db.delete(goal)
