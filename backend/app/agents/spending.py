from datetime import date, timedelta

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.models.transaction import TransactionJournal
from app.models.category import Category


class SpendingAnalystAgent(BaseAgent):
    name = "analista_gastos"
    description = "Analisa padrões de gastos, identifica anomalias e sugere economias"
    icon = "📊"

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        db: AsyncSession = kwargs.get("db")
        if not db:
            return AgentResult(self.name, False, message="Database not available")

        today = date.today()
        first_this = today.replace(day=1)
        first_last = (first_this - timedelta(days=1)).replace(day=1)

        this_spending = await self._total_spending(db, first_this, today)
        last_spending = await self._total_spending(db, first_last, first_this)
        top_cats = await self._top_categories(db, first_this, today)
        subscriptions = await self._detect_subscriptions(db)

        suggestions = self._build_suggestions(this_spending, last_spending, top_cats, subscriptions)

        message = (
            f"Gastos desse mês: R$ {this_spending:.2f} "
            f"({self._format_change(this_spending, last_spending)})"
        )

        return AgentResult(
            self.name, True,
            data={
                "current_month_spending": round(this_spending, 2),
                "last_month_spending": round(last_spending, 2),
                "top_categories": [
                    {"name": c.name or "Sem categoria", "amount": round(float(c.total), 2)}
                    for c in top_cats
                ],
                "change_pct": round(((this_spending - last_spending) / max(last_spending, 1)) * 100, 1),
                "subscriptions_detected": subscriptions,
            },
            message=message,
            suggestions=suggestions,
        )

    async def _total_spending(self, db: AsyncSession, start: date, end: date) -> float:
        result = await db.execute(
            select(func.coalesce(func.sum(TransactionJournal.amount), 0))
            .where(
                TransactionJournal.date >= start,
                TransactionJournal.date < end,
                TransactionJournal.transaction_type == "withdrawal",
            )
        )
        return float(result.scalar() or 0)

    async def _top_categories(self, db: AsyncSession, start: date, end: date):
        result = await db.execute(
            select(
                Category.name,
                func.coalesce(func.sum(TransactionJournal.amount), 0).label("total"),
            )
            .join(Category, TransactionJournal.category_id == Category.id, isouter=True)
            .where(
                TransactionJournal.date >= start,
                TransactionJournal.date < end,
                TransactionJournal.transaction_type == "withdrawal",
            )
            .group_by(Category.name)
            .order_by(func.sum(TransactionJournal.amount).desc())
            .limit(5)
        )
        return result.all()

    async def _detect_subscriptions(self, db: AsyncSession) -> list[dict]:
        today = date.today()
        three_months_ago = today - timedelta(days=90)
        result = await db.execute(
            select(
                TransactionJournal.description,
                TransactionJournal.amount,
                func.count(TransactionJournal.id).label("occurrences"),
            )
            .where(
                TransactionJournal.date >= three_months_ago,
                TransactionJournal.transaction_type == "withdrawal",
                TransactionJournal.amount > 0,
            )
            .group_by(TransactionJournal.description, TransactionJournal.amount)
            .having(func.count(TransactionJournal.id) >= 2)
            .order_by(func.count(TransactionJournal.id).desc())
            .limit(10)
        )
        subs = []
        for r in result.all():
            if r.description and any(k in r.description.lower() for k in
                ["netflix", "spotify", "amazon", "prime", "disney", "hbo", "apple",
                 "google", "microsoft", "office", "adobe", "uber", "ifood", "assinatura",
                 "mensalidade", "plano", "club", "streaming", "youtube"]):
                subs.append({
                    "name": r.description,
                    "amount": round(float(r.amount), 2),
                    "occurrences": r.occurrences,
                })
        return subs

    def _build_suggestions(self, current, last, top_cats, subscriptions) -> list[str]:
        suggestions = []
        if last > 0:
            pct = ((current - last) / last) * 100
            if pct > 20:
                suggestions.append(f"⚠️ Gastos subiram {pct:.0f}% vs mês passado! Revisar urgente.")
            elif pct < -10:
                suggestions.append(f"✅ Gastos caíram {abs(pct):.0f}% vs mês passado. Ótimo trabalho!")

        for cat in top_cats[:3]:
            total = float(cat.total)
            if total > 500:
                suggestions.append(f"💰 R$ {total:.2f} em '{cat.name or 'Sem categoria'}'. Dá pra reduzir?")

        for sub in subscriptions:
            suggestions.append(f"📋 '{sub['name']}' aparece {sub['occurrences']}x. Assinatura de R$ {sub['amount']:.2f}?")

        if not suggestions:
            suggestions.append("📝 Continue registrando gastos para análises personalizadas.")
        return suggestions

    def _format_change(self, current, last) -> str:
        if last == 0:
            return "primeiro mês registrado"
        pct = ((current - last) / last) * 100
        return f"{'+' if pct > 0 else ''}{pct:.0f}% vs mês passado"
