from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.transaction import TransactionJournal, Transaction
from app.models.account import Account

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    first_of_month = today.replace(day=1)

    # Account balances
    accounts_result = await db.execute(
        select(Account).where(Account.is_archived == False)
    )
    accounts = accounts_result.scalars().all()
    total_balance = sum(float(a.balance) for a in accounts)
    total_credit = sum(
        float(a.credit_limit or 0) for a in accounts if a.account_type == "credit_card"
    )

    # Monthly income / expenses
    income_result = await db.execute(
        select(func.coalesce(func.sum(TransactionJournal.amount), 0))
        .where(
            TransactionJournal.date >= first_of_month,
            TransactionJournal.transaction_type == "deposit",
        )
    )
    monthly_income = float(income_result.scalar() or 0)

    expense_result = await db.execute(
        select(func.coalesce(func.sum(TransactionJournal.amount), 0))
        .where(
            TransactionJournal.date >= first_of_month,
            TransactionJournal.transaction_type == "withdrawal",
        )
    )
    monthly_expenses = float(expense_result.scalar() or 0)

    # Recent transactions
    recent_result = await db.execute(
        select(TransactionJournal)
        .order_by(TransactionJournal.date.desc())
        .limit(10)
    )
    recent = recent_result.scalars().all()

    # Upcoming bills (next 7 days)
    next_week = today + timedelta(days=7)
    bills_result = await db.execute(
        select(TransactionJournal)
        .where(
            TransactionJournal.date.between(today, next_week),
            TransactionJournal.transaction_type == "withdrawal",
        )
        .order_by(TransactionJournal.date)
    )
    upcoming = bills_result.scalars().all()

    return {
        "balances": {
            "total": round(total_balance, 2),
            "credit_limit": round(total_credit, 2),
        },
        "monthly": {
            "income": round(monthly_income, 2),
            "expenses": round(monthly_expenses, 2),
            "balance": round(monthly_income - monthly_expenses, 2),
        },
        "recent_transactions": [
            {
                "id": str(j.id),
                "description": j.description,
                "amount": float(j.amount),
                "type": j.transaction_type,
                "date": j.date.isoformat(),
            }
            for j in recent
        ],
        "upcoming_bills": [
            {
                "id": str(j.id),
                "description": j.description,
                "amount": float(j.amount),
                "date": j.date.isoformat(),
            }
            for j in upcoming
        ],
    }


@router.get("/net-worth")
async def net_worth_report(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.is_archived == False)
    )
    accounts = result.scalars().all()

    assets = sum(
        float(a.balance) for a in accounts
        if a.account_type in ("checking", "savings", "investment", "cash")
    )
    liabilities = sum(
        float(a.balance) for a in accounts
        if a.account_type in ("credit_card", "loan", "mortgage")
    )

    return {
        "net_worth": round(assets - liabilities, 2),
        "assets": round(assets, 2),
        "liabilities": round(liabilities, 2),
    }


@router.get("/spending-by-category")
async def spending_by_category(
    month: int | None = None,
    year: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models.category import Category

    today = date.today()
    month = month or today.month
    year = year or today.year

    result = await db.execute(
        select(
            TransactionJournal.category_id,
            Category.name,
            func.coalesce(func.sum(TransactionJournal.amount), 0).label("total"),
        )
        .join(Category, TransactionJournal.category_id == Category.id, isouter=True)
        .where(
            extract("month", TransactionJournal.date) == month,
            extract("year", TransactionJournal.date) == year,
            TransactionJournal.transaction_type == "withdrawal",
        )
        .group_by(TransactionJournal.category_id, Category.name)
        .order_by(func.sum(TransactionJournal.amount).desc())
    )
    rows = result.all()

    total = sum(float(r.total) for r in rows)

    return {
        "month": month,
        "year": year,
        "total": round(total, 2),
        "categories": [
            {
                "name": r.name or "Sem categoria",
                "amount": round(float(r.total), 2),
                "percentage": round(float(r.total) / total * 100, 1) if total > 0 else 0,
            }
            for r in rows
        ],
    }


@router.get("/cash-flow")
async def cash_flow(
    months: int = 6,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    start_date = today.replace(day=1) - timedelta(days=months * 30)

    result = await db.execute(
        select(
            extract("year", TransactionJournal.date).label("year"),
            extract("month", TransactionJournal.date).label("month"),
            TransactionJournal.transaction_type,
            func.coalesce(func.sum(TransactionJournal.amount), 0).label("total"),
        )
        .where(TransactionJournal.date >= start_date)
        .group_by(
            extract("year", TransactionJournal.date),
            extract("month", TransactionJournal.date),
            TransactionJournal.transaction_type,
        )
        .order_by(
            extract("year", TransactionJournal.date),
            extract("month", TransactionJournal.date),
        )
    )
    rows = result.all()

    monthly_data = {}
    for r in rows:
        key = f"{int(r.year)}-{int(r.month):02d}"
        if key not in monthly_data:
            monthly_data[key] = {"month": key, "income": 0, "expenses": 0}
        if r.transaction_type == "deposit":
            monthly_data[key]["income"] = round(float(r.total), 2)
        else:
            monthly_data[key]["expenses"] = round(float(r.total), 2)

    return list(monthly_data.values())
