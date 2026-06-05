from datetime import date, timedelta
from decimal import Decimal
from random import randint

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fincas import MicroSaving, MicroSavingsLog
from app.models.transaction import TransactionJournal, Transaction
from app.models.account import Account
from app.models.goal import Goal


class MicroSavingsEngine:
    """Tsumitate-inspired micro-savings engine.

    Tipos:
    - daily: guarda X reais todo dia
    - weekly: guarda X reais toda semana
    - per_transaction: guarda X reais a cada transação
    - roundup: arredonda cada compra para o valor inteiro acima
    - percent_income: guarda X% de cada depósito
    """

    @staticmethod
    async def execute_savings(db: AsyncSession, savings_id: str) -> dict:
        result = await db.execute(
            select(MicroSaving).where(MicroSaving.id == savings_id, MicroSaving.is_active == True)
        )
        saving = result.scalar_one_or_none()
        if not saving:
            return {"error": "Micro-savings rule not found or inactive"}

        amount = await MicroSavingsEngine._calculate_amount(db, saving)
        if not amount or amount <= 0:
            return {"error": "Amount would be zero", "amount": 0}

        # Create transaction to move money
        if saving.source_account_id and saving.target_account_id:
            journal = TransactionJournal(
                workspace_id=saving.workspace_id,
                transaction_type="transfer",
                description=f"Micro savings: {saving.name}",
                date=date.today(),
                amount=amount,
                currency_code="BRL",
            )
            db.add(journal)
            await db.flush()

            db.add(Transaction(journal_id=journal.id, account_id=saving.source_account_id, amount=-amount, sort_order=1))
            db.add(Transaction(journal_id=journal.id, account_id=saving.target_account_id, amount=amount, sort_order=2))

            log = MicroSavingsLog(micro_savings_id=saving.id, amount=amount, journal_id=journal.id)
        else:
            log = MicroSavingsLog(micro_savings_id=saving.id, amount=amount)

        db.add(log)
        saving.run_count = (saving.run_count or 0) + 1
        saving.total_saved = (saving.total_saved or 0) + amount
        saving.last_run_at = func.now()
        await db.flush()

        # Update linked goal
        if saving.goal_id:
            goal_result = await db.execute(select(Goal).where(Goal.id == saving.goal_id))
            goal = goal_result.scalar_one_or_none()
            if goal:
                goal.current_amount = (goal.current_amount or 0) + amount

        return {"amount": float(amount), "total_saved": float(saving.total_saved), "run_count": saving.run_count}

    @staticmethod
    async def _calculate_amount(db: AsyncSession, saving: MicroSaving) -> Decimal:
        today = date.today()
        stype = saving.savings_type
        config = saving.config or {}
        multiplier = config.get("multiplier", 1)

        if stype == "daily":
            return (saving.amount or Decimal("5.00")) * multiplier

        elif stype == "weekly":
            return (saving.amount or Decimal("20.00")) * multiplier

        elif stype == "percent_income":
            pct = (saving.percentage or Decimal("10.00")) / Decimal("100.00")
            income_result = await db.execute(
                select(func.sum(TransactionJournal.amount)).where(
                    TransactionJournal.workspace_id == saving.workspace_id,
                    TransactionJournal.transaction_type == "deposit",
                    TransactionJournal.date == today,
                )
            )
            income = income_result.scalar() or Decimal("0")
            return (income * pct * multiplier).quantize(Decimal("0.01"))

        elif stype == "roundup":
            threshold = config.get("roundup_threshold", 5.0)
            # Get last transaction amount to calculate round-up
            tx_result = await db.execute(
                select(TransactionJournal.amount)
                .where(
                    TransactionJournal.workspace_id == saving.workspace_id,
                    TransactionJournal.transaction_type == "withdrawal",
                )
                .order_by(TransactionJournal.created_at.desc())
                .limit(1)
            )
            last_amount = tx_result.scalar()
            if not last_amount:
                return Decimal("0")
            last_float = float(last_amount)
            roundup = (int(last_float) + 1) - last_float if last_float != int(last_float) else 0
            total = roundup * multiplier
            # Acorns-style: only execute when cumulative reaches threshold ($5)
            if total < threshold:
                return Decimal("0")
            return Decimal(str(round(total, 2)))

        elif stype == "per_transaction":
            return (saving.amount or Decimal("1.00")) * multiplier

        return Decimal("0")

    @staticmethod
    async def get_stats(db: AsyncSession, workspace_id: str) -> dict:
        result = await db.execute(
            select(
                func.count(MicroSaving.id).label("total_rules"),
                func.sum(MicroSaving.total_saved).label("total_saved"),
                func.sum(MicroSaving.run_count).label("total_runs"),
            ).where(MicroSaving.workspace_id == workspace_id, MicroSaving.is_active == True)
        )
        row = result.one()
        return {
            "active_rules": row.total_rules or 0,
            "total_saved": float(row.total_saved or 0),
            "total_runs": row.total_runs or 0,
        }
