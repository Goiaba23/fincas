from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.fincas import KakeiboEntry, KakeiboSpending, MicroSaving
from app.fincas.kakeibo import KakeiboEngine
from app.fincas.micro_savings import MicroSavingsEngine
from app.fincas.methods import MethodsEngine
from app.models.fincas import KakeiboEntry, KakeiboSpending, MicroSaving

router = APIRouter(prefix="/fincas", tags=["fincas"])


# --- Kakeibo ---

class KakeiboAnswerInput(BaseModel):
    week_start: str | None = None
    q1_available: str | None = None
    q2_save_goal: str | None = None
    q3_spending: str | None = None
    q4_improve: str | None = None
    reflection: str | None = None
    mood: str | None = None


class KakeiboSpendingInput(BaseModel):
    entry_id: str
    category: str
    amount: float
    description: str | None = None
    journal_id: str | None = None


@router.get("/kakeibo/current")
async def get_kakeibo_week(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    entry = await KakeiboEngine.get_or_create_weekly_entry(db, ws_id, str(user.id))
    summary = await KakeiboEngine.get_weekly_summary(db, ws_id, entry.week_start)
    streak = await KakeiboEngine.get_streak(db, ws_id)
    if summary:
        summary["streak"] = streak
    return summary or {"message": "Crie seu primeiro check-in Kakeibo!", "streak": streak}


@router.get("/kakeibo/auto-categorize/{category_name}")
async def auto_categorize(category_name: str):
    mapping = await KakeiboEngine.get_auto_category_mapping(None, category_name)
    return {"category": category_name, "kakeibo_category": mapping, "label": KakeiboEngine.CATEGORY_LABELS[mapping]}


@router.post("/kakeibo/answer")
async def answer_kakeibo(
    body: KakeiboAnswerInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    week_start = date.fromisoformat(body.week_start) if body.week_start else None
    entry = await KakeiboEngine.get_or_create_weekly_entry(db, ws_id, str(user.id), week_start)
    await KakeiboEngine.complete_entry(
        db, str(entry.id),
        q1=body.q1_available, q2=body.q2_save_goal,
        q3=body.q3_spending, q4=body.q4_improve,
        reflection=body.reflection, mood=body.mood,
    )
    await db.commit()
    return {"message": "Kakeibo check-in completed!", "entry_id": str(entry.id)}


@router.post("/kakeibo/spending")
async def add_kakeibo_spending(
    body: KakeiboSpendingInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    spending = await KakeiboEngine.add_spending(
        db, body.entry_id, body.category, body.amount,
        description=body.description, journal_id=body.journal_id,
    )
    await db.commit()
    return {"id": str(spending.id), "category": spending.category, "amount": float(spending.amount)}


# --- Tsumitate / Micro Savings ---

class MicroSavingInput(BaseModel):
    name: str
    savings_type: str
    amount: float | None = None
    percentage: float | None = None
    source_account_id: str | None = None
    target_account_id: str | None = None
    goal_id: str | None = None
    config: dict = {}


@router.post("/micro-savings")
async def create_micro_saving(
    body: MicroSavingInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    saving = MicroSaving(
        workspace_id=ws_id,
        name=body.name,
        savings_type=body.savings_type,
        amount=body.amount,
        percentage=body.percentage,
        source_account_id=body.source_account_id,
        target_account_id=body.target_account_id,
        goal_id=body.goal_id,
        config=body.config,
    )
    db.add(saving)
    await db.commit()
    return {"id": str(saving.id), "name": saving.name, "type": saving.savings_type}


@router.get("/micro-savings")
async def list_micro_savings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    result = await db.execute(
        select(MicroSaving).where(MicroSaving.workspace_id == ws_id).order_by(MicroSaving.created_at.desc())
    )
    savings = result.scalars().all()
    return [
        {
            "id": str(s.id), "name": s.name, "type": s.savings_type,
            "amount": float(s.amount) if s.amount else None,
            "percentage": float(s.percentage) if s.percentage else None,
            "is_active": s.is_active,
            "run_count": s.run_count,
            "total_saved": float(s.total_saved or 0),
        }
        for s in savings
    ]


@router.post("/micro-savings/{savings_id}/execute")
async def execute_micro_saving(
    savings_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await MicroSavingsEngine.execute_savings(db, savings_id)
    await db.commit()
    return result


@router.get("/micro-savings/stats")
async def micro_savings_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    return await MicroSavingsEngine.get_stats(db, ws_id)


# --- Global Methods ---

@router.get("/methods")
async def list_methods():
    return MethodsEngine.get_manifest()


@router.get("/methods/{method_key}")
async def get_method(method_key: str):
    method = MethodsEngine.get_method(method_key)
    if not method:
        raise HTTPException(status_code=404, detail="Method not found")
    return {method_key: method}


@router.get("/lagom")
async def lagom_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    return await MethodsEngine.get_lagom_status(db, ws_id)


@router.get("/desafio-suico")
async def swiss_challenge(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    return await MethodsEngine.get_swiss_challenge_status(db, ws_id)


@router.post("/limpeza-financeira")
async def run_cleanup(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    return await MethodsEngine.run_cleanup_audit(db, ws_id)


# --- Couple Budgeting (Acordo a Dois) ---

@router.get("/acordo-dois")
async def couple_budget_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    workspace: User = Depends(get_current_workspace),
):
    ws_id = str(workspace.id) if hasattr(workspace, 'id') else workspace
    from app.models.workspace import Workspace
    from app.models.user import User as UserModel

    ws_result = await db.execute(select(Workspace).where(Workspace.id == ws_id))
    ws = ws_result.scalar_one_or_none()
    members_result = await db.execute(
        select(UserModel).join(Workspace.workspace_members).where(Workspace.id == ws_id)
    )
    members = members_result.scalars().all()

    return {
        "workspace_name": ws.name if ws else "Unknown",
        "kind": ws.kind if ws else "personal",
        "member_count": len(members),
        "members": [{"id": str(m.id), "name": m.display_name, "email": m.email} for m in members],
        "available_models": [
            {"key": "merged", "name": "Contas Conjuntas", "desc": "Tudo junto, sem separação"},
            {"key": "separate", "name": "Contas Separadas", "desc": "Cada um com sua conta, rateio de despesas"},
            {"key": "hybrid", "name": "Híbrido", "desc": "Conta conjunta para contas, separado para pessoal"},
        ],
    }
