from datetime import date, timedelta

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import TransactionJournal
from app.models.budget import Budget, BudgetLimit
from app.models.goal import Goal
from app.models.category import Category

FINANCE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_accounts",
            "description": "List all accounts with their balances",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_by_category",
            "description": "Get total spending grouped by category for a given month",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {"type": "integer", "description": "Month number (1-12)"},
                    "year": {"type": "integer", "description": "Year (e.g. 2026)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_budgets",
            "description": "Get active budgets with current spending vs limit",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_goals",
            "description": "Get all savings goals with progress",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_monthly_summary",
            "description": "Get a summary of income and expenses for a given month",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {"type": "integer", "description": "Month number (1-12)"},
                    "year": {"type": "integer", "description": "Year (e.g. 2026)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_bills",
            "description": "Get upcoming bills within the next N days",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days ahead"},
                },
            },
        },
    },
]


async def execute_tool(name: str, args: dict, db: AsyncSession) -> str:
    match name:
        case "get_accounts":
            return await _get_accounts(db)
        case "get_spending_by_category":
            return await _get_spending_by_category(db, args.get("month"), args.get("year"))
        case "get_budgets":
            return await _get_budgets(db)
        case "get_goals":
            return await _get_goals(db)
        case "get_monthly_summary":
            return await _get_monthly_summary(db, args.get("month"), args.get("year"))
        case "get_pending_bills":
            return await _get_pending_bills(db, args.get("days", 7))
        case _:
            return f"Unknown tool: {name}"


async def _get_accounts(db: AsyncSession) -> str:
    result = await db.execute(select(Account).where(Account.is_archived == False))
    accounts = result.scalars().all()
    if not accounts:
        return "Nenhuma conta encontrada."
    lines = [f"{a.name}: R$ {float(a.balance):.2f} ({a.account_type})" for a in accounts]
    return "Suas contas:\n" + "\n".join(lines)


async def _get_spending_by_category(db: AsyncSession, month: int | None, year: int | None) -> str:
    today = date.today()
    month = month or today.month
    year = year or today.year

    result = await db.execute(
        select(
            Category.name,
            func.coalesce(func.sum(TransactionJournal.amount), 0).label("total"),
        )
        .join(Category, TransactionJournal.category_id == Category.id, isouter=True)
        .where(
            extract("month", TransactionJournal.date) == month,
            extract("year", TransactionJournal.date) == year,
            TransactionJournal.transaction_type == "withdrawal",
        )
        .group_by(Category.name)
        .order_by(func.sum(TransactionJournal.amount).desc())
    )
    rows = result.all()
    if not rows:
        return f"Nenhum gasto encontrado em {month}/{year}."
    total = sum(float(r.total) for r in rows)
    lines = [f"{r.name or 'Sem categoria'}: R$ {float(r.total):.2f}" for r in rows]
    return f"Gastos de {month}/{year} (total: R$ {total:.2f}):\n" + "\n".join(lines)


async def _get_budgets(db: AsyncSession) -> str:
    result = await db.execute(select(Budget).where(Budget.is_active == True))
    budgets = result.scalars().all()
    if not budgets:
        return "Nenhum orçamento ativo."
    lines = []
    for b in budgets:
        limits_result = await db.execute(
            select(func.sum(BudgetLimit.amount)).where(BudgetLimit.budget_id == b.id)
        )
        total_limit = limits_result.scalar() or 0
        limits_count_result = await db.execute(
            select(func.count(BudgetLimit.id)).where(BudgetLimit.budget_id == b.id)
        )
        limits_count = limits_count_result.scalar() or 0
        lines.append(f"{b.name}: {limits_count} categorias, R$ {float(total_limit):.2f} limite")
    return "Orçamentos:\n" + "\n".join(lines)


async def _get_goals(db: AsyncSession) -> str:
    result = await db.execute(select(Goal).where(Goal.is_completed == False))
    goals = result.scalars().all()
    if not goals:
        return "Nenhuma meta ativa."
    lines = []
    for g in goals:
        pct = (float(g.current_amount) / float(g.target_amount) * 100) if g.target_amount > 0 else 0
        lines.append(f"{g.name}: R$ {float(g.current_amount):.2f} / R$ {float(g.target_amount):.2f} ({pct:.0f}%)")
    return "Metas:\n" + "\n".join(lines)


async def _get_monthly_summary(db: AsyncSession, month: int | None, year: int | None) -> str:
    today = date.today()
    month = month or today.month
    year = year or today.year

    income = await db.execute(
        select(func.coalesce(func.sum(TransactionJournal.amount), 0))
        .where(
            extract("month", TransactionJournal.date) == month,
            extract("year", TransactionJournal.date) == year,
            TransactionJournal.transaction_type == "deposit",
        )
    )
    expenses = await db.execute(
        select(func.coalesce(func.sum(TransactionJournal.amount), 0))
        .where(
            extract("month", TransactionJournal.date) == month,
            extract("year", TransactionJournal.date) == year,
            TransactionJournal.transaction_type == "withdrawal",
        )
    )
    inc = float(income.scalar() or 0)
    exp = float(expenses.scalar() or 0)
    return (
        f"Resumo de {month}/{year}:\n"
        f"• Receitas: R$ {inc:.2f}\n"
        f"• Despesas: R$ {exp:.2f}\n"
        f"• Saldo: R$ {inc - exp:.2f}"
    )


async def _get_pending_bills(db: AsyncSession, days: int) -> str:
    today = date.today()
    end = today + timedelta(days=days)
    result = await db.execute(
        select(TransactionJournal)
        .where(
            TransactionJournal.date.between(today, end),
            TransactionJournal.transaction_type == "withdrawal",
        )
        .order_by(TransactionJournal.date)
    )
    bills = result.scalars().all()
    if not bills:
        return f"Nenhuma conta próxima nos próximos {days} dias."
    lines = [f"{b.description or 'Sem descrição'}: R$ {float(b.amount):.2f} em {b.date}" for b in bills]
    return f"Contas dos próximos {days} dias ({len(bills)}):\n" + "\n".join(lines)
