from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.models.subscription import Subscription

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

PLAN_MONTHLY_PRICE = 40
TRIAL_DAYS = 7


@router.get("/status")
async def get_subscription_status(
    db: AsyncSession = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.workspace_id == workspace.id)
        .order_by(Subscription.created_at.desc())
    )
    sub = result.scalars().first()

    now = datetime.now(timezone.utc)

    if sub is None:
        return {
            "status": "none",
            "plan": None,
            "trial_days_remaining": 0,
            "has_access": False,
            "message": "Nenhuma assinatura encontrada. Ative seu trial grátis!",
        }

    is_trial = sub.status == "trial" and sub.trial_end and sub.trial_end > now
    is_active = sub.status == "active" and sub.current_period_end and sub.current_period_end > now
    is_expired = sub.status in ("trial", "active") and not is_trial and not is_active
    is_canceled = sub.status == "canceled"

    trial_days_left = 0
    if is_trial and sub.trial_end:
        trial_days_left = max(0, (sub.trial_end - now).days)

    return {
        "id": str(sub.id),
        "status": sub.status,
        "plan": sub.plan_code,
        "trial_days_remaining": trial_days_left,
        "trial_started": sub.trial_started_at.isoformat() if sub.trial_started_at else None,
        "trial_ends": sub.trial_end.isoformat() if sub.trial_end else None,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
        "has_access": is_trial or is_active,
        "is_expired": is_expired,
        "is_canceled": is_canceled,
        "price_monthly": PLAN_MONTHLY_PRICE,
        "message": _status_message(is_trial, is_active, is_expired, is_canceled, trial_days_left),
    }


@router.post("/start-trial")
async def start_trial(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.workspace_id == workspace.id)
        .order_by(Subscription.created_at.desc())
    )
    existing = result.scalars().first()

    if existing and existing.status in ("trial", "active"):
        raise HTTPException(status_code=400, detail="Você já possui uma assinatura ativa ou trial em andamento")

    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=TRIAL_DAYS)

    sub = Subscription(
        workspace_id=workspace.id,
        provider="manual",
        plan_code="monthly_40",
        status="trial",
        current_period_start=now,
        current_period_end=trial_end,
        trial_started_at=now,
        trial_end=trial_end,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)

    return {
        "id": str(sub.id),
        "status": "trial",
        "trial_days": TRIAL_DAYS,
        "trial_ends": trial_end.isoformat(),
        "message": f"Trial grátis de {TRIAL_DAYS} dias ativado! Aproveite todos os recursos.",
    }


@router.post("/activate")
async def activate_subscription(
    db: AsyncSession = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.workspace_id == workspace.id)
        .order_by(Subscription.created_at.desc())
    )
    sub = result.scalars().first()
    if not sub:
        raise HTTPException(status_code=404, detail="Nenhuma assinatura encontrada")

    now = datetime.now(timezone.utc)
    period_end = now + timedelta(days=30)

    sub.status = "active"
    sub.provider = "manual"
    sub.plan_code = "monthly_40"
    sub.current_period_start = now
    sub.current_period_end = period_end
    sub.cancel_at = None
    sub.canceled_at = None

    await db.commit()

    return {
        "status": "active",
        "current_period_end": period_end.isoformat(),
        "message": "Assinatura ativada com sucesso!",
    }


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.workspace_id == workspace.id)
        .order_by(Subscription.created_at.desc())
    )
    sub = result.scalars().first()
    if not sub:
        raise HTTPException(status_code=404, detail="Nenhuma assinatura encontrada")

    now = datetime.now(timezone.utc)
    sub.status = "canceled"
    sub.canceled_at = now

    await db.commit()

    return {"status": "canceled", "message": "Assinatura cancelada. Você terá acesso até o fim do período."}


def _status_message(
    is_trial: bool, is_active: bool, is_expired: bool, is_canceled: bool, trial_days_left: int
) -> str:
    if is_trial:
        return f"🎯 Trial grátis — {trial_days_left} dia(s) restantes"
    if is_active:
        return "✅ Plano ativo — todos os recursos liberados"
    if is_expired:
        return "⏰ Período expirado — renove para continuar usando"
    if is_canceled:
        return "🛑 Assinatura cancelada"
    return "📋 Ative seu trial grátis de 7 dias"
