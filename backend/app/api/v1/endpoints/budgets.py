from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.budget import Budget, BudgetLimit
from app.services.envelope_budget import get_envelope_state, assign_to_envelope, get_envelope_month_history

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetCreate(BaseModel):
    name: str
    budget_type: str = "envelope"
    currency_code: str = "BRL"
    monthly_income: float = 0


class LimitCreate(BaseModel):
    budget_id: str
    category_id: str
    amount: float
    period: str = "monthly"
    start_date: date
    end_date: date | None = None
    is_carryover: bool = False


class EnvelopeAssign(BaseModel):
    budget_id: str
    category_id: str
    amount: float
    month: str


@router.get("/")
async def list_budgets(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Budget).where(Budget.is_active == True).order_by(Budget.created_at.desc())
    )
    budgets = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "type": b.budget_type,
            "currency": b.currency_code,
            "monthly_income": float(b.monthly_income or 0),
            "ready_to_assign": float(b.ready_to_assign or 0),
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
        monthly_income=req.monthly_income,
    )
    db.add(budget)
    await db.flush()
    return {"id": str(budget.id), "name": budget.name}


@router.get("/{budget_id}")
async def get_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
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
        "monthly_income": float(budget.monthly_income or 0),
        "ready_to_assign": float(budget.ready_to_assign or 0),
        "limits": [
            {
                "id": str(l.id),
                "category_id": str(l.category_id),
                "amount": float(l.amount),
                "period": l.period,
                "start_date": l.start_date.isoformat(),
                "is_carryover": l.is_carryover,
            }
            for l in limits
        ],
    }


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
    await db.flush()
    return {"id": str(limit.id), "amount": float(limit.amount)}


@router.get("/{budget_id}/envelopes")
async def get_envelopes(
    budget_id: UUID,
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(404)

    state = await get_envelope_state(db, budget_id, year, month, budget.workspace_id)
    return state


@router.get("/{budget_id}/envelopes/{category_id}/history")
async def envelope_history(
    budget_id: UUID,
    category_id: UUID,
    months: int = Query(6),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    history = await get_envelope_month_history(db, budget_id, category_id, months)
    return {"category_id": str(category_id), "history": history}


@router.post("/envelopes/assign", status_code=201)
async def assign_envelope(
    req: EnvelopeAssign,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    month_parts = req.month.split("-")
    month_date = date(int(month_parts[0]), int(month_parts[1]), 1)
    result = await assign_to_envelope(db, UUID(req.budget_id), UUID(req.category_id), req.amount, month_date)
    return result
