from uuid import UUID
from datetime import date, timedelta
from calendar import monthrange

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget, BudgetLimit
from app.models.transaction import TransactionJournal
from app.models.category import Category


async def get_envelope_state(
    db: AsyncSession,
    budget_id: UUID,
    year: int,
    month: int,
    workspace_id: UUID,
) -> dict:
    budget = await db.get(Budget, budget_id)
    if not budget:
        return {"error": "Budget not found"}

    first_day = date(year, month, 1)
    _, last_day_num = monthrange(year, month)
    last_day = date(year, month, last_day_num)

    limits_result = await db.execute(
        select(BudgetLimit).where(
            BudgetLimit.budget_id == budget_id,
            BudgetLimit.start_date <= last_day,
            (BudgetLimit.end_date.is_(None) | (BudgetLimit.end_date >= first_day)),
        )
    )
    limits = limits_result.scalars().all()

    txn_result = await db.execute(
        select(
            TransactionJournal.category_id,
            func.coalesce(func.sum(TransactionJournal.amount), 0).label("total_activity"),
        )
        .where(
            TransactionJournal.workspace_id == workspace_id,
            TransactionJournal.date >= first_day,
            TransactionJournal.date <= last_day,
        )
        .group_by(TransactionJournal.category_id)
    )
    txn_rows = {str(row[0]): float(row[1]) for row in txn_result if row[0]}

    categories_result = await db.execute(
        select(Category).order_by(Category.sort_order)
    )
    categories = {str(c.id): c for c in categories_result.scalars().all()}

    envelopes = []
    for limit in limits:
        cat_id_str = str(limit.category_id)
        activity = txn_rows.get(cat_id_str, 0) or 0
        assigned = float(limit.amount)
        available = assigned + activity

        carryover = 0.0
        if limit.is_carryover and month > 1:
            prev_month = month - 1
            prev_year = year
            if prev_month == 0:
                prev_month = 12
                prev_year -= 1
            carryover = await _get_carryover(
                db, limit.category_id, prev_year, prev_month, workspace_id, assigned, limit
            )
            available += carryover

        cat = categories.get(cat_id_str)
        envelopes.append({
            "category_id": cat_id_str,
            "category_name": cat.name if cat else "Unknown",
            "category_color": cat.color if cat else None,
            "group_id": str(cat.group_id) if cat else None,
            "assigned": assigned,
            "activity": activity,
            "available": available,
            "carryover": carryover,
            "is_carryover_enabled": limit.is_carryover,
        })

    return {
        "budget_id": str(budget_id),
        "budget_name": budget.name,
        "year": year,
        "month": month,
        "total_assigned": sum(e["assigned"] for e in envelopes),
        "total_activity": sum(e["activity"] for e in envelopes),
        "total_available": sum(e["available"] for e in envelopes),
        "envelopes": envelopes,
        "currency": budget.currency_code,
    }


async def _get_carryover(
    db: AsyncSession,
    category_id: UUID,
    year: int,
    month: int,
    workspace_id: UUID,
    prev_assigned: float,
    limit: BudgetLimit,
) -> float:
    first_day = date(year, month, 1)
    _, last_day_num = monthrange(year, month)
    last_day = date(year, month, last_day_num)

    txn_result = await db.execute(
        select(func.coalesce(func.sum(TransactionJournal.amount), 0))
        .where(
            TransactionJournal.workspace_id == workspace_id,
            TransactionJournal.category_id == category_id,
            TransactionJournal.date >= first_day,
            TransactionJournal.date <= last_day,
        )
    )
    prev_activity = float(txn_result.scalar() or 0)
    return prev_assigned + prev_activity


async def assign_to_envelope(
    db: AsyncSession,
    budget_id: UUID,
    category_id: UUID,
    amount: float,
    month: date,
) -> dict:
    limit_result = await db.execute(
        select(BudgetLimit).where(
            BudgetLimit.budget_id == budget_id,
            BudgetLimit.category_id == category_id,
        )
    )
    limit = limit_result.scalar_one_or_none()
    if limit:
        limit.amount = amount
    else:
        budget = await db.get(Budget, budget_id)
        if not budget:
            return {"error": "Budget not found"}
        limit = BudgetLimit(
            budget_id=budget_id,
            category_id=category_id,
            amount=amount,
            period="monthly",
            start_date=month,
        )
        db.add(limit)

    return {"category_id": str(category_id), "assigned": amount, "month": month.isoformat()}


async def get_envelope_month_history(
    db: AsyncSession,
    budget_id: UUID,
    category_id: UUID,
    months: int = 6,
) -> list:
    from datetime import datetime
    today = date.today()
    history = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m < 1:
            m += 12
            y -= 1
        while m > 12:
            m -= 12
            y += 1

        first_day = date(y, m, 1)
        _, last = monthrange(y, m)
        last_day = date(y, m, last)

        txn_result = await db.execute(
            select(func.coalesce(func.sum(TransactionJournal.amount), 0))
            .where(
                TransactionJournal.category_id == category_id,
                TransactionJournal.date >= first_day,
                TransactionJournal.date <= last_day,
            )
        )
        activity = float(txn_result.scalar() or 0)

        limit_result = await db.execute(
            select(BudgetLimit).where(
                BudgetLimit.budget_id == budget_id,
                BudgetLimit.category_id == category_id,
                BudgetLimit.start_date <= last_day,
                (BudgetLimit.end_date.is_(None) | (BudgetLimit.end_date >= first_day)),
            )
        )
        limit = limit_result.scalar_one_or_none()
        assigned = float(limit.amount) if limit else 0

        history.append({
            "month": f"{y}-{m:02d}",
            "assigned": assigned,
            "activity": activity,
            "available": assigned + activity,
        })

    return history
