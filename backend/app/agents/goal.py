from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.models.goal import Goal


class GoalAgent(BaseAgent):
    name = "analista_metas"
    description = "Acompanha progresso de metas financeiras e motiva o usuário"
    icon = "🏆"

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        db: AsyncSession = kwargs.get("db")
        if not db:
            return AgentResult(self.name, False, message="Database not available")

        result = await db.execute(
            select(Goal).where(Goal.is_completed == False)
        )
        goals = result.scalars().all()

        if not goals:
            return AgentResult(
                self.name, True,
                data={"goals": []},
                message="Nenhuma meta ativa. Que tal criar uma?",
                suggestions=["Crie uma meta! Ex: 'Economizar R$ 5.000 para viagem'."],
            )

        goal_data = []
        suggestions = []

        for g in goals:
            target = float(g.target_amount)
            current = float(g.current_amount)
            pct = (current / target * 100) if target > 0 else 0
            remaining = target - current
            deadline = g.deadline

            if deadline:
                days_left = (deadline - date.today()).days
            else:
                days_left = None

            goal_data.append({
                "name": g.name,
                "target": round(target, 2),
                "current": round(current, 2),
                "percentage": round(pct, 1),
                "remaining": round(remaining, 2),
                "deadline": deadline.isoformat() if deadline else None,
                "days_left": days_left,
            })

            if pct >= 100:
                suggestions.append(f"🎉 Meta '{g.name}' concluída! Parabéns!")
            elif pct >= 75:
                suggestions.append(f"🚀 Meta '{g.name}' quase lá! Faltam R$ {remaining:.2f}.")
            elif days_left and days_left < 30 and pct < 50:
                suggestions.append(f"⏰ Meta '{g.name}' vence em {days_left} dias e só {pct:.0f}% concluída. Acelere!")
            elif days_left and days_left < 0:
                suggestions.append(f"⌛ Meta '{g.name}' venceu! Reavalie o prazo ou valor.")

        if not suggestions:
            suggestions.append("Continue firme nas suas metas! Cada depósito conta.")

        return AgentResult(
            self.name, True,
            data={"goals": goal_data},
            message=f"{len(goals)} meta(s) ativa(s)",
            suggestions=suggestions,
        )
