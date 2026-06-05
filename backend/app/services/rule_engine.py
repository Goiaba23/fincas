import re
from uuid import UUID
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import RuleGroup, Rule, RuleTrigger, RuleAction


TRIGGER_TYPE_DESCRIPTION_CONTAINS = "description_contains"
TRIGGER_TYPE_DESCRIPTION_MATCHES = "description_matches"
TRIGGER_TYPE_DESCRIPTION_STARTS = "description_starts"
TRIGGER_TYPE_DESCRIPTION_ENDS = "description_ends"
TRIGGER_TYPE_AMOUNT_GREATER = "amount_greater_than"
TRIGGER_TYPE_AMOUNT_LESS = "amount_less_than"
TRIGGER_TYPE_AMOUNT_EQUALS = "amount_equals"
TRIGGER_TYPE_TYPE_IS = "type_is"
TRIGGER_TYPE_DATE_AFTER = "date_after"
TRIGGER_TYPE_DATE_BEFORE = "date_before"
TRIGGER_TYPE_PAYEE_IS = "payee_is"
TRIGGER_TYPE_CATEGORY_IS = "category_is"

ACTION_TYPE_SET_CATEGORY = "set_category"
ACTION_TYPE_SET_PAYEE = "set_payee"
ACTION_TYPE_SET_DESCRIPTION = "set_description"
ACTION_TYPE_SET_TYPE = "set_type"
ACTION_TYPE_ADD_NOTE = "add_note"
ACTION_TYPE_SET_TAG = "set_tag"
ACTION_TYPE_LINK_RULE = "link_rule"


async def execute_rules(
    db: AsyncSession,
    workspace_id: UUID,
    transaction_data: dict,
) -> dict:
    groups_result = await db.execute(
        select(RuleGroup)
        .where(
            RuleGroup.workspace_id == workspace_id,
            RuleGroup.is_active == True,
        )
        .order_by(RuleGroup.sort_order)
    )
    groups = groups_result.scalars().all()

    modified = dict(transaction_data)
    matched_rules = []

    for group in groups:
        rules_result = await db.execute(
            select(Rule)
            .where(
                Rule.group_id == group.id,
                Rule.is_active == True,
            )
            .order_by(Rule.sort_order)
        )
        rules = rules_result.scalars().all()

        for rule in rules:
            triggers_result = await db.execute(
                select(RuleTrigger).where(RuleTrigger.rule_id == rule.id).order_by(RuleTrigger.sort_order)
            )
            triggers = triggers_result.scalars().all()

            if not triggers:
                continue

            if _evaluate_triggers(triggers, modified):
                actions_result = await db.execute(
                    select(RuleAction).where(RuleAction.rule_id == rule.id).order_by(RuleAction.sort_order)
                )
                actions = actions_result.scalars().all()

                for action in actions:
                    _execute_action(action, modified)

                matched_rules.append({
                    "rule_id": str(rule.id),
                    "rule_name": rule.name,
                    "group_name": group.name,
                })

                if rule.stop_processing:
                    break
        else:
            continue
        break

    modified["matched_rules"] = matched_rules
    return modified


def _evaluate_triggers(triggers: list[RuleTrigger], txn: dict) -> bool:
    for trigger in triggers:
        result = _evaluate_single_trigger(trigger, txn)
        if trigger.is_negated:
            result = not result
        if not result:
            return False
    return True


def _evaluate_single_trigger(trigger: RuleTrigger, txn: dict) -> bool:
    t = trigger.trigger_type
    val = trigger.value.lower().strip() if trigger.value else ""

    if t == TRIGGER_TYPE_DESCRIPTION_CONTAINS:
        desc = (txn.get("description") or "").lower()
        return val in desc

    elif t == TRIGGER_TYPE_DESCRIPTION_MATCHES:
        desc = (txn.get("description") or "")
        try:
            return bool(re.search(val, desc, re.IGNORECASE))
        except re.error:
            return False

    elif t == TRIGGER_TYPE_DESCRIPTION_STARTS:
        desc = (txn.get("description") or "").lower()
        return desc.startswith(val)

    elif t == TRIGGER_TYPE_DESCRIPTION_ENDS:
        desc = (txn.get("description") or "").lower()
        return desc.endswith(val)

    elif t == TRIGGER_TYPE_AMOUNT_GREATER:
        return float(txn.get("amount", 0)) > float(val)

    elif t == TRIGGER_TYPE_AMOUNT_LESS:
        return float(txn.get("amount", 0)) < float(val)

    elif t == TRIGGER_TYPE_AMOUNT_EQUALS:
        return abs(float(txn.get("amount", 0)) - float(val)) < 0.01

    elif t == TRIGGER_TYPE_TYPE_IS:
        return (txn.get("transaction_type") or "").lower() == val

    elif t == TRIGGER_TYPE_DATE_AFTER:
        txn_date = txn.get("date")
        if isinstance(txn_date, date):
            return txn_date > datetime.strptime(val, "%Y-%m-%d").date()
        return False

    elif t == TRIGGER_TYPE_DATE_BEFORE:
        txn_date = txn.get("date")
        if isinstance(txn_date, date):
            return txn_date < datetime.strptime(val, "%Y-%m-%d").date()
        return False

    elif t == TRIGGER_TYPE_PAYEE_IS:
        return str(txn.get("payee_id", "")).lower() == val

    elif t == TRIGGER_TYPE_CATEGORY_IS:
        return str(txn.get("category_id", "")).lower() == val

    return True


def _execute_action(action: RuleAction, txn: dict):
    t = action.action_type
    val = action.value

    if t == ACTION_TYPE_SET_CATEGORY and val:
        txn["category_id"] = val
    elif t == ACTION_TYPE_SET_PAYEE and val:
        txn["payee_id"] = val
    elif t == ACTION_TYPE_SET_DESCRIPTION and val:
        txn["description"] = val
    elif t == ACTION_TYPE_SET_TYPE and val:
        txn["transaction_type"] = val
    elif t == ACTION_TYPE_ADD_NOTE and val:
        existing = txn.get("notes") or ""
        txn["notes"] = (existing + "\n" + val).strip()
    elif t == ACTION_TYPE_SET_TAG and val:
        tags = txn.get("tags") or []
        if isinstance(tags, list) and val not in tags:
            tags.append(val)
        elif isinstance(tags, str) and tags:
            txn["tags"] = tags + "," + val
        else:
            txn["tags"] = val


async def test_rule_on_transaction(
    db: AsyncSession,
    rule_id: UUID,
    test_data: dict,
) -> dict:
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        return {"error": "Rule not found"}

    triggers_result = await db.execute(
        select(RuleTrigger).where(RuleTrigger.rule_id == rule_id).order_by(RuleTrigger.sort_order)
    )
    triggers = triggers_result.scalars().all()

    actions_result = await db.execute(
        select(RuleAction).where(RuleAction.rule_id == rule_id).order_by(RuleAction.sort_order)
    )
    actions = actions_result.scalars().all()

    triggered = _evaluate_triggers(triggers, test_data)

    modified = dict(test_data)
    if triggered:
        for action in actions:
            _execute_action(action, modified)

    return {
        "rule_name": rule.name,
        "triggered": triggered,
        "input": test_data,
        "output": modified,
    }
