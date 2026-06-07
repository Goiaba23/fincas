from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.account import Account

router = APIRouter(prefix="/accounts", tags=["accounts"])


class AccountCreate(BaseModel):
    name: str
    account_type: str
    currency_code: str = "BRL"
    balance: float = 0
    color: str | None = None
    icon: str | None = None
    credit_limit: float | None = None
    card_brand: str | None = None
    card_last_digits: str | None = None
    statement_close_day: int | None = None
    statement_due_day: int | None = None


@router.get("/")
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.workspace_id.isnot(None)).order_by(Account.sort_order).limit(100)
    )
    accounts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "type": a.account_type,
            "balance": float(a.balance),
            "currency_code": a.currency_code,
            "credit_limit": float(a.credit_limit) if a.credit_limit else None,
            "card_brand": a.card_brand,
            "card_last_digits": a.card_last_digits,
            "color": a.color,
            "icon": a.icon,
            "statement_close_day": a.statement_close_day,
            "statement_due_day": a.statement_due_day,
        }
        for a in accounts
    ]


@router.post("/", status_code=201)
async def create_account(
    req: AccountCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    account = Account(
        workspace_id=user.id,
        name=req.name,
        account_type=req.account_type,
        currency_code=req.currency_code,
        balance=req.balance,
        color=req.color,
        icon=req.icon,
        credit_limit=req.credit_limit,
        card_brand=req.card_brand,
        card_last_digits=req.card_last_digits,
        statement_close_day=req.statement_close_day,
        statement_due_day=req.statement_due_day,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return {
        "id": str(account.id),
        "name": account.name,
        "type": account.account_type,
        "balance": float(account.balance),
        "currency_code": account.currency_code,
        "credit_limit": float(account.credit_limit) if account.credit_limit else None,
        "card_brand": account.card_brand,
        "card_last_digits": account.card_last_digits,
        "color": account.color,
        "icon": account.icon,
        "statement_close_day": account.statement_close_day,
        "statement_due_day": account.statement_due_day,
    }
