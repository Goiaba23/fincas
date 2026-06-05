from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.transaction import TransactionJournal, Transaction
from app.models.account import Account
from app.services.rule_engine import execute_rules

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    description: str
    amount: float
    transaction_type: str
    date: date
    account_id: str
    category_id: str | None = None
    payee_id: str | None = None
    notes: str | None = None
    tags: list[str] | None = None
    skip_rules: bool = False


class TransactionOut(BaseModel):
    id: str
    description: str | None
    amount: float
    transaction_type: str
    date: str
    account_id: str | None
    category_id: str | None
    payee_id: str | None
    notes: str | None
    matched_rules: list | None = None


@router.get("/")
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    result = await db.execute(
        select(TransactionJournal)
        .order_by(TransactionJournal.date.desc(), TransactionJournal.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    journals = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "description": j.description,
            "amount": float(j.amount),
            "type": j.transaction_type,
            "date": j.date.isoformat(),
            "category_id": str(j.category_id) if j.category_id else None,
            "payee_id": str(j.payee_id) if j.payee_id else None,
            "notes": j.notes,
        }
        for j in journals
    ]


@router.post("/", status_code=201)
async def create_transaction(
    req: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    txn_data = {
        "description": req.description,
        "amount": req.amount,
        "transaction_type": req.transaction_type,
        "date": req.date,
        "account_id": req.account_id,
        "category_id": req.category_id,
        "payee_id": req.payee_id,
        "notes": req.notes,
        "tags": req.tags or [],
    }

    if not req.skip_rules:
        account = await db.get(Account, req.account_id)
        if account:
            txn_data = await execute_rules(db, account.workspace_id, txn_data)

    journal = TransactionJournal(
        description=txn_data["description"],
        amount=txn_data["amount"],
        transaction_type=txn_data["transaction_type"],
        date=txn_data["date"],
        currency_code="BRL",
        payee_id=txn_data.get("payee_id"),
        category_id=txn_data.get("category_id"),
        notes=txn_data.get("notes"),
        workspace_id=None,
    )
    db.add(journal)
    await db.flush()

    account = await db.get(Account, req.account_id)
    if account:
        journal.workspace_id = account.workspace_id

    sign = -1 if txn_data["transaction_type"] == "withdrawal" else 1
    txn = Transaction(
        journal_id=journal.id,
        account_id=req.account_id,
        amount=sign * txn_data["amount"],
    )
    db.add(txn)

    result = {
        "id": str(journal.id),
        "description": journal.description,
        "amount": float(txn.amount),
        "transaction_type": journal.transaction_type,
        "date": journal.date.isoformat(),
        "account_id": req.account_id,
        "category_id": str(journal.category_id) if journal.category_id else None,
        "payee_id": str(journal.payee_id) if journal.payee_id else None,
        "notes": journal.notes,
    }

    if not req.skip_rules:
        result["matched_rules"] = txn_data.get("matched_rules", [])

    return result
