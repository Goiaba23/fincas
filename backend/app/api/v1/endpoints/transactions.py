from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.transaction import TransactionJournal, Transaction
from app.models.account import Account

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    description: str
    amount: float
    transaction_type: str
    date: date
    account_id: str
    category_id: str | None = None
    payee_id: str | None = None


@router.get("/")
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TransactionJournal).order_by(TransactionJournal.date.desc()).limit(50)
    )
    journals = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "description": j.description,
            "amount": float(j.amount),
            "type": j.transaction_type,
            "date": j.date.isoformat(),
        }
        for j in journals
    ]


@router.post("/", status_code=201)
async def create_transaction(
    req: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    journal = TransactionJournal(
        description=req.description,
        amount=req.amount,
        transaction_type=req.transaction_type,
        date=req.date,
        currency_code="BRL",
        payee_id=req.payee_id,
        category_id=req.category_id,
    )
    db.add(journal)
    await db.flush()

    txn = Transaction(
        journal_id=journal.id,
        account_id=req.account_id,
        amount=-req.amount if req.transaction_type == "withdrawal" else req.amount,
    )
    db.add(txn)

    return {"id": str(journal.id), "description": journal.description, "amount": float(journal.amount)}
