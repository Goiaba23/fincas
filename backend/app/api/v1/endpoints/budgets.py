from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.budget import Budget, BudgetLimit

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetCreate(BaseModel):
    name: str
    budget_type: str = "envelope"
    currency_code: str = "BRL"


class LimitCreate(BaseModel):
    budget_id: str
    category_id: str
    amount: float
    period: str = "monthly"
    start_date: date
    end_date: date | None = None
    is_carryover: bool = False


# --- Budgets ---

@router.get("/")
async def list_budgets(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Budget).where(Budget.is_active == True)
    )
    budgets = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "type": b.budget_type,
            "currency": b.currency_code,
            "limit_count": 0,
        }
        for b in budgets
    ]


@router.post("/", status_code=201)
async def create_budget(
    req: BudgetCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    budget = Budget(
        name=req.name,
        budget_type=req.budget_type,
        currency_code=req.currency_code,
    )
    db.add(budget)
    return {"id": str(budget.id), "name": budget.name}


@router.get("/{budget_id}")
async def get_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(404)

    limits_result = await db.execute(
        select(BudgetLimit).where(BudgetLimit.budget_id == budget_id)
    )
    limits = limits_result.scalars().all()

    return {
        "id": str(budget.id),
        "name": budget.name,
        "type": budget.budget_type,
        "currency": budget.currency_code,
        "limits": [
            {
                "id": str(l.id),
                "category_id": str(l.category_id),
                "amount": float(l.amount),
                "period": l.period,
                "start_date": l.start_date.isoformat(),
            }
            for l in limits
        ],
    }


# --- Budget Limits ---

@router.post("/limits", status_code=201)
async def set_budget_limit(
    req: LimitCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit = BudgetLimit(
        budget_id=req.budget_id,
        category_id=req.category_id,
        amount=req.amount,
        period=req.period,
        start_date=req.start_date,
        end_date=req.end_date,
        is_carryover=req.is_carryover,
    )
    db.add(limit)
    return {"id": str(limit.id), "amount": float(limit.amount)}
