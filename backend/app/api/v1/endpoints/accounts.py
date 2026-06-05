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


@router.get("/")
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.workspace_id.isnot(None)).limit(100)
    )
    accounts = result.scalars().all()
    return [{"id": str(a.id), "name": a.name, "type": a.account_type, "balance": float(a.balance)} for a in accounts]


@router.post("/", status_code=201)
async def create_account(
    req: AccountCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    account = Account(
        workspace_id=user.id,  # placeholder - real workspace resolution needed
        name=req.name,
        account_type=req.account_type,
        currency_code=req.currency_code,
        balance=req.balance,
        color=req.color,
        icon=req.icon,
    )
    db.add(account)
    await db.flush()
    return {"id": str(account.id), "name": account.name}
