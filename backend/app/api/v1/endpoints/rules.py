from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.rule import RuleGroup, Rule, RuleTrigger, RuleAction
from app.services.rule_engine import execute_rules, test_rule_on_transaction

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


class TestRuleInput(BaseModel):
    description: str = ""
    amount: float = 0
    transaction_type: str = "withdrawal"
    date: date | None = None
    category_id: str | None = None
    payee_id: str | None = None


@router.get("/groups")
async def list_rule_groups(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RuleGroup).where(RuleGroup.is_active == True).order_by(RuleGroup.sort_order)
    )
    groups = result.scalars().all()
    result_data = []
    for g in groups:
        count_result = await db.execute(
            select(Rule).where(Rule.group_id == g.id, Rule.is_active == True)
        )
        result_data.append({
            "id": str(g.id),
            "name": g.name,
            "description": g.description,
            "rule_count": len(count_result.scalars().all()),
        })
    return result_data


@router.post("/groups", status_code=201)
async def create_rule_group(
    req: GroupCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = RuleGroup(name=req.name, description=req.description)
    db.add(group)
    await db.flush()
    return {"id": str(group.id), "name": group.name}


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
    await db.flush()
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
        select(RuleTrigger).where(RuleTrigger.rule_id == rule_id).order_by(RuleTrigger.sort_order)
    )
    actions = await db.execute(
        select(RuleAction).where(RuleAction.rule_id == rule_id).order_by(RuleAction.sort_order)
    )

    return {
        "id": str(rule.id),
        "name": rule.name,
        "group_id": str(rule.group_id),
        "description": rule.description,
        "stop_processing": rule.stop_processing,
        "triggers": [
            {"id": str(t.id), "type": t.trigger_type, "value": t.value, "is_negated": t.is_negated}
            for t in triggers.scalars()
        ],
        "actions": [
            {"id": str(a.id), "type": a.action_type, "value": a.value}
            for a in actions.scalars()
        ],
    }


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
    await db.flush()
    return {"id": str(trigger.id), "type": trigger.trigger_type, "value": trigger.value}


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
    await db.flush()
    return {"id": str(action.id), "type": action.action_type, "value": action.value}


@router.post("/{rule_id}/test")
async def test_rule(
    rule_id: UUID,
    test_data: TestRuleInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    txn_dict = test_data.model_dump()
    txn_dict["date"] = txn_dict["date"] or date.today()
    result = await test_rule_on_transaction(db, rule_id, txn_dict)
    return result
