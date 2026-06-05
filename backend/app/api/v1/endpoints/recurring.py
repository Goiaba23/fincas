from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.recurring import RecurringTransaction, Bill

router = APIRouter(prefix="/recurring", tags=["recurring"])


class RecurringCreate(BaseModel):
    description: str
    transaction_type: str
    amount: float
    source_account_id: str | None = None
    dest_account_id: str | None = None
    category_id: str | None = None
    payee_id: str | None = None
    frequency: str
    interval_count: int = 1
    start_date: date
    end_date: date | None = None
    auto_create: bool = True
    notes: str | None = None


class BillCreate(BaseModel):
    name: str
    amount_min: float
    amount_max: float | None = None
    date: date
    repeat_freq: str | None = None
    category_id: str | None = None
    account_id: str | None = None
    payee_id: str | None = None


# --- Recurring Transactions ---

@router.get("/transactions")
async def list_recurring(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RecurringTransaction).where(RecurringTransaction.is_active == True)
    )
    items = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "description": r.description,
            "amount": float(r.amount),
            "frequency": r.frequency,
            "next": r.next_occurrence.isoformat() if r.next_occurrence else None,
            "auto_create": r.auto_create,
        }
        for r in items
    ]


@router.post("/transactions", status_code=201)
async def create_recurring(
    req: RecurringCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rt = RecurringTransaction(
        description=req.description,
        transaction_type=req.transaction_type,
        amount=req.amount,
        source_account_id=req.source_account_id,
        dest_account_id=req.dest_account_id,
        category_id=req.category_id,
        payee_id=req.payee_id,
        frequency=req.frequency,
        interval_count=req.interval_count,
        start_date=req.start_date,
        end_date=req.end_date,
        auto_create=req.auto_create,
        notes=req.notes,
        next_occurrence=req.start_date,
    )
    db.add(rt)
    return {"id": str(rt.id), "description": rt.description}


# --- Bills ---

@router.get("/bills")
async def list_bills(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Bill).where(Bill.is_active == True)
    )
    bills = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "amount_min": float(b.amount_min),
            "amount_max": float(b.amount_max) if b.amount_max else None,
            "date": b.date.isoformat(),
            "repeat_freq": b.repeat_freq,
        }
        for b in bills
    ]


@router.post("/bills", status_code=201)
async def create_bill(
    req: BillCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bill = Bill(
        name=req.name,
        amount_min=req.amount_min,
        amount_max=req.amount_max,
        date=req.date,
        repeat_freq=req.repeat_freq,
        category_id=req.category_id,
        account_id=req.account_id,
        payee_id=req.payee_id,
    )
    db.add(bill)
    return {"id": str(bill.id), "name": bill.name}
