import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token
from app.core.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.subscription import Subscription

router = APIRouter(prefix="/auth", tags=["auth"])

TRIAL_DAYS = 7


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.display_name,
    )
    db.add(user)
    await db.flush()

    ws = Workspace(name=f"{req.display_name}", created_by=user.id)
    db.add(ws)
    await db.flush()

    member = WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner")
    db.add(member)
    await db.flush()

    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=TRIAL_DAYS)
    sub = Subscription(
        workspace_id=ws.id,
        provider="manual",
        plan_code="monthly_40",
        status="trial",
        current_period_start=now,
        current_period_end=trial_end,
        trial_started_at=now,
        trial_end=trial_end,
    )
    db.add(sub)
    await db.flush()

    return {"id": str(user.id), "email": user.email, "display_name": user.display_name}


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")

    token = create_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)


@router.get("/me")
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.models.workspace import WorkspaceMember
    result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = result.scalars().first()
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "locale": user.locale,
        "currency_code": user.currency_code,
        "workspace_id": str(membership.workspace_id) if membership else None,
    }
