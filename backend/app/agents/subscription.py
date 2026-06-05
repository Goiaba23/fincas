from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.models.transaction import TransactionJournal


class SubscriptionDetectiveAgent(BaseAgent):
    name = "detetive_assinaturas"
    description = "Detecta assinaturas recorrentes e calcula gasto mensal total"
    icon = "🔍"

    KEYWORDS = [
        "netflix", "spotify", "amazon", "prime", "disney", "hbo", "apple",
        "google", "microsoft", "office", "adobe", "uber one", "ifood", "assinatura",
        "mensalidade", "plano", "club", "streaming", "youtube", "paramount",
        "crunchyroll", "dropbox", "notion", "figma", "canva", "medium",
        "linkedin", "github copilot", "chatgpt", "openai", "claude",
    ]

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        db: AsyncSession = kwargs.get("db")
        if not db:
            return AgentResult(self.name, False, message="Database not available")

        six_months_ago = date.today() - timedelta(days=180)

        result = await db.execute(
            select(
                func.lower(TransactionJournal.description).label("desc"),
                TransactionJournal.amount,
                func.count(TransactionJournal.id).label("occurrences"),
            )
            .where(
                TransactionJournal.date >= six_months_ago,
                TransactionJournal.transaction_type == "withdrawal",
                TransactionJournal.amount.between(1, 500),
            )
            .group_by(func.lower(TransactionJournal.description), TransactionJournal.amount)
            .having(func.count(TransactionJournal.id) >= 2)
            .order_by(func.count(TransactionJournal.id).desc())
        )
        rows = result.all()

        subscriptions = []
        total_monthly = 0
        suggestions = []

        for r in rows:
            desc = r.desc or ""
            if not any(k in desc for k in self.KEYWORDS):
                continue

            subscriptions.append({
                "name": desc.strip(),
                "amount": round(float(r.amount), 2),
                "occurrences": r.occurrences,
                "frequency": "mensal" if r.occurrences >= 3 else "recorrente",
            })
            total_monthly += float(r.amount)

        if subscriptions:
            suggestions.append(f"📋 Você tem {len(subscriptions)} assinatura(s) — total de R$ {total_monthly:.2f}/mês (R$ {total_monthly * 12:.2f}/ano).")
            expensive = [s for s in subscriptions if s["amount"] > 50]
            for s in expensive[:2]:
                suggestions.append(f"✂️ '{s['name']}' custa R$ {s['amount']:.2f}/mês. Usa o suficiente?")
            if len(subscriptions) > 5:
                suggestions.append(f"🔴 {len(subscriptions)} assinaturas é muito! Reveja se usa todas.")
            else:
                suggestions.append("✅ Número de assinaturas sob controle.")

        return AgentResult(
            self.name, True,
            data={
                "subscriptions": subscriptions,
                "total_monthly": round(total_monthly, 2),
                "total_yearly": round(total_monthly * 12, 2),
                "count": len(subscriptions),
            },
            message=f"{len(subscriptions)} assinatura(s): R$ {total_monthly:.2f}/mês" if subscriptions else "Nenhuma assinatura detectada",
            suggestions=suggestions,
        )
