from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.rule import RuleGroup, Rule, RuleTrigger, RuleAction

router = APIRouter(prefix="/rules", tags=["rules"])


class GroupCreate(BaseModel):
    name: str
    description: str | None = None


class RuleCreate(BaseModel):
    group_id: str
    name: str
    description: str | None = None
    stop_processing: bool = False


class TriggerCreate(BaseModel):
    rule_id: str
    trigger_type: str
    value: str
    is_negated: bool = False


class ActionCreate(BaseModel):
    rule_id: str
    action_type: str
    value: str | None = None


# --- Rule Groups ---

@router.get("/groups")
async def list_rule_groups(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RuleGroup).where(RuleGroup.is_active == True).order_by(RuleGroup.sort_order)
    )
    groups = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "name": g.name,
            "description": g.description,
            "rule_count": 0,
        }
        for g in groups
    ]


@router.post("/groups", status_code=201)
async def create_rule_group(
    req: GroupCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = RuleGroup(name=req.name, description=req.description)
    db.add(group)
    return {"id": str(group.id), "name": group.name}


# --- Rules ---

@router.get("/")
async def list_rules(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Rule).where(Rule.is_active == True).order_by(Rule.sort_order)
    )
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "group_id": str(r.group_id),
            "description": r.description,
            "stop_processing": r.stop_processing,
        }
        for r in rules
    ]


@router.post("/", status_code=201)
async def create_rule(
    req: RuleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rule = Rule(
        group_id=req.group_id,
        name=req.name,
        description=req.description,
        stop_processing=req.stop_processing,
    )
    db.add(rule)
    return {"id": str(rule.id), "name": rule.name}


@router.get("/{rule_id}")
async def get_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404)

    triggers = await db.execute(
        select(RuleTrigger).where(RuleTrigger.rule_id == rule_id)
    )
    actions = await db.execute(
        select(RuleAction).where(RuleAction.rule_id == rule_id)
    )

    return {
        "id": str(rule.id),
        "name": rule.name,
        "triggers": [
            {"type": t.trigger_type, "value": t.value} for t in triggers.scalars()
        ],
        "actions": [
            {"type": a.action_type, "value": a.value} for a in actions.scalars()
        ],
    }


# --- Triggers ---

@router.post("/triggers", status_code=201)
async def add_trigger(
    req: TriggerCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trigger = RuleTrigger(
        rule_id=req.rule_id,
        trigger_type=req.trigger_type,
        value=req.value,
        is_negated=req.is_negated,
    )
    db.add(trigger)
    return {"id": str(trigger.id), "type": trigger.trigger_type, "value": trigger.value}


# --- Actions ---

@router.post("/actions", status_code=201)
async def add_action(
    req: ActionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    action = RuleAction(
        rule_id=req.rule_id,
        action_type=req.action_type,
        value=req.value,
    )
    db.add(action)
    return {"id": str(action.id), "type": action.action_type, "value": action.value}
