from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fincas import KakeiboEntry, KakeiboSpending
from app.models.transaction import TransactionJournal


class KakeiboEngine:
    """Japanese Kakeibo method: 4 questions, 4 categories, weekly reflection.

    - 4 perguntas: Quanto tenho? Quanto quero poupar? Quanto gasto? Como melhorar?
    - 4 categorias: essential, wants, culture, unexpected
    - Check-in semanal com reflexão e mood
    """

    CATEGORIES = ["essential", "wants", "culture", "unexpected"]
    CATEGORY_LABELS = {
        "essential": "Essenciais (moradia, comida, transporte)",
        "wants": "Desejos (lazer, restaurantes, hobbies)",
        "culture": "Cultura (livros, museus, cursos)",
        "unexpected": "Imprevistos (reparos, emergências)",
    }

    @staticmethod
    async def get_or_create_weekly_entry(
        db: AsyncSession, workspace_id: str, user_id: str, week_start: date | None = None
    ) -> KakeiboEntry:
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        result = await db.execute(
            select(KakeiboEntry).where(
                KakeiboEntry.workspace_id == workspace_id,
                KakeiboEntry.user_id == user_id,
                KakeiboEntry.week_start == week_start,
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            return entry

        # Auto-calculate totals from transactions
        week_end = week_start + timedelta(days=6)
        income_result = await db.execute(
            select(func.sum(TransactionJournal.amount)).where(
                TransactionJournal.workspace_id == workspace_id,
                TransactionJournal.date.between(week_start, week_end),
                TransactionJournal.transaction_type == "deposit",
            )
        )
        total_income = income_result.scalar() or Decimal("0.00")

        expense_result = await db.execute(
            select(func.sum(TransactionJournal.amount)).where(
                TransactionJournal.workspace_id == workspace_id,
                TransactionJournal.date.between(week_start, week_end),
                TransactionJournal.transaction_type == "withdrawal",
            )
        )
        total_expenses = expense_result.scalar() or Decimal("0.00")

        entry = KakeiboEntry(
            workspace_id=workspace_id,
            user_id=user_id,
            week_start=week_start,
            total_income=total_income,
            total_expenses=total_expenses,
            savings_amount=max(Decimal("0.00"), total_income - total_expenses),
        )
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def add_spending(
        db: AsyncSession,
        entry_id: str,
        category: str,
        amount: Decimal,
        description: str | None = None,
        journal_id: str | None = None,
    ) -> KakeiboSpending:
        if category not in KakeiboEngine.CATEGORIES:
            raise ValueError(f"Categoria inválida: {category}. Use: {KakeiboEngine.CATEGORIES}")

        spending = KakeiboSpending(
            entry_id=entry_id,
            category=category,
            amount=amount,
            description=description,
            journal_id=journal_id,
        )
        db.add(spending)
        await db.flush()
        return spending

    @staticmethod
    async def complete_entry(
        db: AsyncSession,
        entry_id: str,
        q1: str | None = None,
        q2: str | None = None,
        q3: str | None = None,
        q4: str | None = None,
        reflection: str | None = None,
        mood: str | None = None,
    ) -> KakeiboEntry:
        result = await db.execute(select(KakeiboEntry).where(KakeiboEntry.id == entry_id))
        entry = result.scalar_one_or_none()
        if not entry:
            raise ValueError("Kakeibo entry not found")

        entry.q1_available = q1
        entry.q2_save_goal = q2
        entry.q3_spending = q3
        entry.q4_improve = q4
        entry.reflection = reflection
        entry.mood = mood
        await db.flush()
        return entry

    @staticmethod
    async def get_weekly_summary(db: AsyncSession, workspace_id: str, week_start: date | None = None):
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        result = await db.execute(
            select(KakeiboEntry).where(
                KakeiboEntry.workspace_id == workspace_id,
                KakeiboEntry.week_start == week_start,
            )
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None

        spending_result = await db.execute(
            select(
                KakeiboSpending.category,
                func.sum(KakeiboSpending.amount).label("total"),
                func.count(KakeiboSpending.id).label("count"),
            )
            .where(KakeiboSpending.entry_id == entry.id)
            .group_by(KakeiboSpending.category)
        )
        spending_by_cat = {row.category: {"total": float(row.total), "count": row.count} for row in spending_result.all()}

        week_end = week_start + timedelta(days=6)
        actual_tx = await db.execute(
            select(
                TransactionJournal.transaction_type,
                func.sum(TransactionJournal.amount).label("total"),
                func.count(TransactionJournal.id).label("count"),
            )
            .where(
                TransactionJournal.workspace_id == workspace_id,
                TransactionJournal.date.between(week_start, week_end),
            )
            .group_by(TransactionJournal.transaction_type)
        )
        actuals = {row.transaction_type: float(row.total) for row in actual_tx.all()}

        historical = await db.execute(
            select(func.avg(KakeiboEntry.savings_amount)).where(
                KakeiboEntry.workspace_id == workspace_id,
                KakeiboEntry.week_start < week_start,
            )
        )
        avg_savings = float(historical.scalar() or 0)

        return {
            "id": str(entry.id),
            "week_start": entry.week_start.isoformat(),
            "total_income": float(entry.total_income or 0),
            "actual_income": actuals.get("deposit", 0),
            "total_expenses": float(entry.total_expenses or 0),
            "actual_expenses": actuals.get("withdrawal", 0),
            "savings_amount": float(entry.savings_amount or 0),
            "savings_rate": round(float(entry.savings_amount or 0) / float(entry.total_income or 1) * 100, 1),
            "avg_weekly_savings": round(avg_savings, 2),
            "vs_average": round(float(entry.savings_amount or 0) - avg_savings, 2),
            "mood": entry.mood,
            "spending_by_category": spending_by_cat,
            "questions": {
                "q1_available": entry.q1_available,
                "q2_save_goal": entry.q2_save_goal,
                "q3_spending": entry.q3_spending,
                "q4_improve": entry.q4_improve,
            },
            "reflection": entry.reflection,
        }

    @staticmethod
    async def get_auto_category_mapping(user_id: str, category_name: str) -> str:
        essential = {"aluguel", "condomínio", "água", "luz", "gás", "supermercado", "farmácia",
                     "plano de saúde", "escola", "faculdade", "transporte", "gasolina", "uber"}
        wants = {"restaurante", "ifood", "delivery", "bar", "cerveja", "cinema", "shopping",
                 "roupa", "sapato", "jogo", "steam", "netflix", "spotify", "hbo"}
        culture = {"livro", "curso", "udemy", "museu", "show", "teatro", "ingresso", "assinatura"}
        name_lower = category_name.lower()
        for kw in essential:
            if kw in name_lower:
                return "essential"
        for kw in wants:
            if kw in name_lower:
                return "wants"
        for kw in culture:
            if kw in name_lower:
                return "culture"
        return "unexpected"

    @staticmethod
    async def get_streak(db: AsyncSession, workspace_id: str) -> dict:
        result = await db.execute(
            select(KakeiboEntry).where(
                KakeiboEntry.workspace_id == workspace_id,
                KakeiboEntry.q1_available.isnot(None),
            ).order_by(KakeiboEntry.week_start.desc())
        )
        entries = result.scalars().all()
        streak = 0
        for e in entries:
            if e.mood != "struggling":
                streak += 1
            else:
                break
        return {"current_streak": streak, "total_weeks": len(entries)}
