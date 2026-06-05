from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_current_workspace(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Workspace:
    result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="No workspace found for user")

    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == membership.workspace_id)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


async def require_active_subscription(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
) -> None:
    from datetime import datetime, timezone
    from app.models.subscription import Subscription
    result = await db.execute(
        select(Subscription)
        .where(Subscription.workspace_id == workspace.id)
        .order_by(Subscription.created_at.desc())
    )
    sub = result.scalars().first()
    if not sub:
        raise HTTPException(
            status_code=402,
            detail="Assinatura necessária. Ative seu trial grátis de 7 dias.",
        )
    now = datetime.now(timezone.utc)
    is_trial = sub.status == "trial" and sub.trial_end and sub.trial_end > now
    is_active = sub.status == "active" and sub.current_period_end and sub.current_period_end > now
    if not is_trial and not is_active:
        raise HTTPException(
            status_code=402,
            detail="Sua assinatura expirou. Renove para continuar usando.",
        )
