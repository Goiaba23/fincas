from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.models.account import Account
from app.models.transaction import TransactionJournal


class DebtAgent(BaseAgent):
    name = "consultor_dividas"
    description = "Analisa dívidas e sugere estratégias de pagamento (bola de neve / avalanche)"
    icon = "💳"

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        db: AsyncSession = kwargs.get("db")
        if not db:
            return AgentResult(self.name, False, message="Database not available")

        result = await db.execute(
            select(Account).where(
                Account.account_type.in_(["credit_card", "loan", "mortgage"]),
                Account.is_archived == False,
            )
        )
        debt_accounts = result.scalars().all()

        if not debt_accounts:
            return AgentResult(
                self.name, True,
                data={"debts": [], "total_debt": 0},
                message="Nenhuma dívida registrada! 🎉",
                suggestions=["Mantenha-se assim! Crie metas de emergência com o dinheiro que sobra."],
            )

        debts = []
        total = 0
        suggestions = []

        for acc in debt_accounts:
            balance = float(acc.balance)
            if balance >= 0:
                continue
            total += abs(balance)
            debts.append({
                "name": acc.name,
                "balance": round(balance, 2),
                "limit": round(float(acc.credit_limit or 0), 2),
                "type": acc.account_type,
                "usage_pct": round(abs(balance) / float(acc.credit_limit or 1) * 100, 1) if acc.credit_limit else 0,
            })

        if not debts:
            return AgentResult(self.name, True, data={"debts": [], "total_debt": 0},
                               message="Nenhuma dívida ativa!", suggestions=[])

        total_formatted = f"R$ {total:,.2f}"
        suggestions.append(f"💳 Dívida total: {total_formatted}.")

        high_interest = [d for d in debts if d["type"] == "credit_card"]
        if high_interest:
            suggestions.append("🔥 Priorize cartões de crédito — são as dívidas com juros mais altos (até 400% ao ano!).")

        # Get monthly income for context
        today = date.today()
        first_month = today.replace(day=1)
        income_result = await db.execute(
            select(func.coalesce(func.sum(TransactionJournal.amount), 0))
            .where(
                TransactionJournal.date >= first_month,
                TransactionJournal.transaction_type == "deposit",
            )
        )
        monthly_income = float(income_result.scalar() or 0)

        if monthly_income > 0:
            debt_income_ratio = (total / monthly_income) * 100
            if debt_income_ratio > 50:
                suggestions.append(f"⚠️ Sua dívida é {debt_income_ratio:.0f}% da sua renda mensal. Busque ajuda financeira.")
            elif debt_income_ratio > 30:
                suggestions.append(f"📊 Dívida representa {debt_income_ratio:.0f}% da renda. Tente manter abaixo de 30%.")
            else:
                suggestions.append(f"✅ Dívida controlada: {debt_income_ratio:.0f}% da renda.")

            # Snowball vs Avalanche recommendation
            min_payment = total * 0.05  # estimated minimum
            if min_payment < monthly_income * 0.3:
                suggestions.append(f"💰 Com R$ {min_payment:.0f}/mês (5% da dívida), você quita em ~{(total / max(min_payment, 1)):.0f} meses.")

        return AgentResult(
            self.name, True,
            data={
                "debts": debts,
                "total_debt": round(total, 2),
                "monthly_income": round(monthly_income, 2),
                "debt_to_income_ratio": round((total / max(monthly_income, 1)) * 100, 1),
            },
            message=f"Dívida total: {total_formatted} em {len(debts)} conta(s)",
            suggestions=suggestions,
        )
