from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.payee import Payee

router = APIRouter(prefix="/payees", tags=["payees"])


class PayeeCreate(BaseModel):
    name: str
    category_id: str | None = None
    is_merchant: bool = True


class PayeeUpdate(BaseModel):
    name: str | None = None
    category_id: str | None = None


@router.get("/")
async def list_payees(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Payee).order_by(Payee.name)
    )
    payees = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "category_id": str(p.category_id) if p.category_id else None,
            "is_merchant": p.is_merchant,
            "transaction_count": 0,
        }
        for p in payees
    ]


@router.post("/", status_code=201)
async def create_payee(
    req: PayeeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    payee = Payee(
        name=req.name,
        category_id=req.category_id,
        is_merchant=req.is_merchant,
    )
    db.add(payee)
    return {"id": str(payee.id), "name": payee.name}


@router.patch("/{payee_id}")
async def update_payee(
    payee_id: str,
    req: PayeeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Payee).where(Payee.id == payee_id))
    payee = result.scalar_one_or_none()
    if not payee:
        raise HTTPException(404)

    if req.name:
        payee.name = req.name
    if req.category_id is not None:
        payee.category_id = req.category_id

    return {"id": str(payee.id), "name": payee.name}
