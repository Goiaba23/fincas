from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.credit_card import CreditCardBill

router = APIRouter(prefix="/credit-cards", tags=["credit_cards"])


class PayBillRequest(BaseModel):
    paid_amount: float


@router.get("/bills")
async def list_bills(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CreditCardBill)
        .order_by(CreditCardBill.due_date.desc())
        .limit(50)
    )
    bills = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "account_id": str(b.account_id),
            "closing_date": b.closing_date.isoformat(),
            "due_date": b.due_date.isoformat(),
            "total": float(b.total_amount),
            "minimum": float(b.minimum_payment) if b.minimum_payment else None,
            "paid": float(b.paid_amount),
            "status": b.status,
        }
        for b in bills
    ]


@router.get("/bills/upcoming")
async def upcoming_bills(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    result = await db.execute(
        select(CreditCardBill)
        .where(
            CreditCardBill.due_date >= today,
            CreditCardBill.status.in_(["open", "closed"]),
        )
        .order_by(CreditCardBill.due_date)
    )
    bills = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "due_date": b.due_date.isoformat(),
            "total": float(b.total_amount),
            "days_until_due": (b.due_date - today).days,
        }
        for b in bills
    ]


@router.post("/bills/{bill_id}/pay")
async def pay_bill(
    bill_id: UUID,
    req: PayBillRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CreditCardBill).where(CreditCardBill.id == bill_id)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(404)

    bill.paid_amount = req.paid_amount
    bill.status = "paid" if req.paid_amount >= float(bill.total_amount) else "partial"
    bill.paid_at = None  # will be set by trigger

    return {"id": str(bill.id), "status": bill.status, "paid": float(bill.paid_amount)}
