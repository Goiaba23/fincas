from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.models.budget import Budget, BudgetLimit
from app.models.transaction import TransactionJournal
from app.models.category import Category


class BudgetAgent(BaseAgent):
    name = "analista_orcamentos"
    description = "Acompanha orçamentos, alerta estouros e sugere realocações"
    icon = "🎯"

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        db: AsyncSession = kwargs.get("db")
        if not db:
            return AgentResult(self.name, False, message="Database not available")

        today = date.today()
        first_of_month = today.replace(day=1)

        result = await db.execute(
            select(Budget).where(Budget.is_active == True)
        )
        budgets = result.scalars().all()

        if not budgets:
            return AgentResult(
                self.name, True,
                data={"budgets": []},
                message="Nenhum orçamento ativo. Crie um para controlar seus gastos!",
                suggestions=["Crie um orçamento mensal para começar a controlar seus gastos."],
            )

        budget_statuses = []
        total_budget = 0
        total_spent = 0
        suggestions = []

        for budget in budgets:
            limits_result = await db.execute(
                select(BudgetLimit).where(BudgetLimit.budget_id == budget.id)
            )
            limits = limits_result.scalars().all()

            spent = 0
            for limit in limits:
                cat_result = await db.execute(
                    select(func.coalesce(func.sum(TransactionJournal.amount), 0))
                    .where(
                        TransactionJournal.category_id == limit.category_id,
                        TransactionJournal.date >= first_of_month,
                        TransactionJournal.transaction_type == "withdrawal",
                    )
                )
                spent += float(cat_result.scalar() or 0)

            total_budget += float(budget.total_limit or 0)
            total_spent += spent
            pct = (spent / float(budget.total_limit or 1)) * 100 if budget.total_limit else 0

            budget_statuses.append({
                "name": budget.name,
                "limit": round(float(budget.total_limit or 0), 2),
                "spent": round(spent, 2),
                "remaining": round(float(budget.total_limit or 0) - spent, 2),
                "percentage": round(pct, 1),
            })

            if pct > 90:
                suggestions.append(f"🔴 Orçamento '{budget.name}' quase estourou ({pct:.0f}% usado)!")
            elif pct > 75:
                suggestions.append(f"🟡 Orçamento '{budget.name}' em {pct:.0f}%. Fique de olho.")

        if total_budget > 0:
            total_pct = (total_spent / total_budget) * 100
            if total_pct < 50:
                days_left = (date(today.year, today.month + 1, 1) - today).days - 1 if today.month < 12 else 0
                daily_remaining = (total_budget - total_spent) / max(days_left, 1)
                suggestions.append(f"💡 Ainda restam R$ {total_budget - total_spent:.2f} do orçamento. R$ {daily_remaining:.2f}/dia até o fim do mês.")

        return AgentResult(
            self.name, True,
            data={"budgets": budget_statuses, "total_budget": round(total_budget, 2), "total_spent": round(total_spent, 2)},
            message=f"{len(budgets)} orçamento(s) ativo(s) — R$ {total_spent:.0f} usado de R$ {total_budget:.0f}",
            suggestions=suggestions,
        )
