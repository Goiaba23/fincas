from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import TransactionJournal
from app.models.category import Category, CategoryGroup
from app.models.goal import Goal
from app.models.budget import Budget, BudgetLimit
from app.models.workspace import WorkspaceMethod


class DashboardService:
    def __init__(self, db: AsyncSession, workspace_id: str):
        self.db = db
        self.workspace_id = workspace_id

    async def get_balance(self) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Account.balance), 0))
            .where(Account.workspace_id == self.workspace_id)
            .where(Account.is_archived == False)
        )
        return float(result.scalar())

    async def get_monthly_summary(self) -> dict:
        today = date.today()
        month_start = today.replace(day=1)

        income_result = await self.db.execute(
            select(func.coalesce(func.sum(TransactionJournal.amount), 0))
            .where(TransactionJournal.workspace_id == self.workspace_id)
            .where(TransactionJournal.transaction_type == "deposit")
            .where(TransactionJournal.date >= month_start)
            .where(TransactionJournal.date <= today)
        )
        income = float(income_result.scalar())

        expense_result = await self.db.execute(
            select(func.coalesce(func.sum(TransactionJournal.amount), 0))
            .where(TransactionJournal.workspace_id == self.workspace_id)
            .where(TransactionJournal.transaction_type == "withdrawal")
            .where(TransactionJournal.date >= month_start)
            .where(TransactionJournal.date <= today)
        )
        expense = float(expense_result.scalar())

        savings_rate = ((income - expense) / income * 100) if income > 0 else 0

        return {
            "income": round(income, 2),
            "expense": round(expense, 2),
            "net": round(income - expense, 2),
            "savings_rate": round(savings_rate, 1),
        }

    async def get_category_breakdown(self) -> list[dict]:
        today = date.today()
        month_start = today.replace(day=1)

        query = (
            select(
                Category.name,
                CategoryGroup.name.label("group_name"),
                func.coalesce(func.sum(TransactionJournal.amount), 0).label("total"),
            )
            .join(CategoryGroup, Category.group_id == CategoryGroup.id)
            .join(TransactionJournal, TransactionJournal.category_id == Category.id)
            .where(TransactionJournal.workspace_id == self.workspace_id)
            .where(TransactionJournal.transaction_type == "withdrawal")
            .where(TransactionJournal.date >= month_start)
            .where(TransactionJournal.date <= today)
            .group_by(Category.id, CategoryGroup.name)
            .order_by(func.sum(TransactionJournal.amount).desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        total = sum(float(r.total) for r in rows) if rows else 0

        return [
            {
                "category": r.name,
                "group": r.group_name,
                "amount": round(float(r.total), 2),
                "percentage": round((float(r.total) / total * 100), 1) if total > 0 else 0,
            }
            for r in rows
        ]

    async def get_recent_transactions(self, limit: int = 10) -> list[dict]:
        query = (
            select(
                TransactionJournal,
                Category.name.label("category_name"),
            )
            .outerjoin(Category, TransactionJournal.category_id == Category.id)
            .where(TransactionJournal.workspace_id == self.workspace_id)
            .order_by(TransactionJournal.date.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "id": str(r.TransactionJournal.id),
                "description": r.TransactionJournal.description,
                "amount": float(r.TransactionJournal.amount),
                "type": r.TransactionJournal.transaction_type,
                "date": r.TransactionJournal.date.isoformat(),
                "category": r.category_name,
            }
            for r in rows
        ]

    async def get_goals(self) -> list[dict]:
        result = await self.db.execute(
            select(Goal)
            .where(Goal.workspace_id == self.workspace_id)
            .order_by(Goal.is_completed.asc(), Goal.sort_order.asc())
        )
        goals = result.scalars().all()

        return [
            {
                "id": str(g.id),
                "name": g.name,
                "target_amount": float(g.target_amount),
                "current_amount": float(g.current_amount),
                "progress_pct": round(float(g.current_amount) / float(g.target_amount) * 100, 1)
                if g.target_amount > 0
                else 0,
                "is_completed": g.is_completed,
            }
            for g in goals
        ]

    async def get_budget_progress(self) -> list[dict]:
        today = date.today()
        month_start = today.replace(day=1)

        result = await self.db.execute(
            select(Budget)
            .options(selectinload(Budget.limits).selectinload(BudgetLimit.category))
            .where(
                Budget.workspace_id == self.workspace_id,
                Budget.is_active == True,
            )
        )
        budgets = result.scalars().all()

        items = []
        for budget in budgets:
            for limit in budget.limits:
                spent_result = await self.db.execute(
                    select(func.coalesce(func.sum(TransactionJournal.amount), 0))
                    .where(TransactionJournal.workspace_id == self.workspace_id)
                    .where(TransactionJournal.category_id == limit.category_id)
                    .where(TransactionJournal.transaction_type == "withdrawal")
                    .where(TransactionJournal.date >= month_start)
                    .where(TransactionJournal.date <= today)
                )
                spent = float(spent_result.scalar())
                budgeted = float(limit.amount)

                items.append(
                    {
                        "category_id": str(limit.category_id),
                        "category_name": limit.category.name if limit.category else "Desconhecida",
                        "budgeted": budgeted,
                        "spent": round(spent, 2),
                        "remaining": round(budgeted - spent, 2),
                        "progress_pct": round(spent / budgeted * 100, 1) if budgeted > 0 else 0,
                    }
                )

        return items

    async def get_net_worth_history(self, months: int = 6) -> list[dict]:
        today = date.today()
        points = []

        current_balance = await self.get_balance()

        for i in range(months - 1, -1, -1):
            month_date = today - relativedelta(months=i)
            month_end = month_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
            if month_end > today:
                month_end = today

            income_result = await self.db.execute(
                select(func.coalesce(func.sum(TransactionJournal.amount), 0))
                .where(TransactionJournal.workspace_id == self.workspace_id)
                .where(TransactionJournal.transaction_type == "deposit")
                .where(TransactionJournal.date >= month_date.replace(day=1))
                .where(TransactionJournal.date <= month_end)
            )
            income = float(income_result.scalar())

            expense_result = await self.db.execute(
                select(func.coalesce(func.sum(TransactionJournal.amount), 0))
                .where(TransactionJournal.workspace_id == self.workspace_id)
                .where(TransactionJournal.transaction_type == "withdrawal")
                .where(TransactionJournal.date >= month_date.replace(day=1))
                .where(TransactionJournal.date <= month_end)
            )
            expense = float(expense_result.scalar())

            points.append(
                {
                    "month": month_date.strftime("%b"),
                    "year": month_date.year,
                    "income": round(income, 2),
                    "expense": round(expense, 2),
                    "net": round(income - expense, 2),
                    "date": month_date.isoformat(),
                }
            )

        return points

    async def get_balance_sparkline(self) -> list[dict]:
        today = date.today()
        points = []

        for i in range(11, -1, -1):
            month_date = today - relativedelta(months=i)
            income_result = await self.db.execute(
                select(func.coalesce(func.sum(TransactionJournal.amount), 0))
                .where(TransactionJournal.workspace_id == self.workspace_id)
                .where(TransactionJournal.transaction_type == "deposit")
                .where(
                    TransactionJournal.date >= month_date.replace(day=1),
                    TransactionJournal.date
                    <= (month_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)),
                )
            )
            expense_result = await self.db.execute(
                select(func.coalesce(func.sum(TransactionJournal.amount), 0))
                .where(TransactionJournal.workspace_id == self.workspace_id)
                .where(TransactionJournal.transaction_type == "withdrawal")
                .where(
                    TransactionJournal.date >= month_date.replace(day=1),
                    TransactionJournal.date
                    <= (month_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)),
                )
            )
            net = float(income_result.scalar()) - float(expense_result.scalar())
            points.append({"month": month_date.strftime("%b"), "value": round(net, 2)})

        return points

    async def get_active_method(self) -> str | None:
        result = await self.db.execute(
            select(WorkspaceMethod.method)
            .where(WorkspaceMethod.workspace_id == self.workspace_id)
            .where(WorkspaceMethod.is_enabled == True)
            .order_by(WorkspaceMethod.created_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row

    async def get_full_dashboard(self) -> dict:
        balance = await self.get_balance()
        monthly = await self.get_monthly_summary()
        active_method = await self.get_active_method()
        categories = await self.get_category_breakdown()
        transactions = await self.get_recent_transactions()
        goals = await self.get_goals()
        budget = await self.get_budget_progress()
        history = await self.get_net_worth_history()
        sparkline = await self.get_balance_sparkline()

        return {
            "active_method": active_method,
            "balance": balance,
            "monthly": monthly,
            "category_breakdown": categories,
            "recent_transactions": transactions,
            "goals": goals,
            "budget_progress": budget,
            "net_worth_history": history,
            "balance_sparkline": sparkline,
        }
