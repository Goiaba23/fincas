from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import TransactionJournal
from app.models.goal import Goal
from app.models.credit_card import CreditCardBill


METHODS_MANIFEST = {
    "kakeibo": {
        "name": "Kakeibo",
        "origin": "Japão (1904)",
        "icon": "japan",
        "description": "Método japonês de 4 perguntas e 4 categorias para gastar com mindfulness. Reduz gastos em 25-35%.",
        "how_it_works": "Check-in semanal: quanto tenho? quanto quero poupar? quanto estou gastando? como melhorar?",
        "benefits": ["Reduz gastos supérfluos", "Aumenta consciência financeira", "Cria hábito de reflexão"],
        "features": ["4 perguntas reflexivas", "4 categorias essenciais/desejos/cultura/imprevistos", "Auto-categorização inteligente", "Histórico de streak"],
    },
    "tsumitate": {
        "name": "Tsumitate",
        "origin": "Japão (NISA)",
        "icon": "piggy-bank",
        "description": "Poupança automática em pequenas quantias consistentes. Inspirado no Tsumitate NISA e Acorns Round-Ups.",
        "how_it_works": "Todo dia/semana, uma pequena quantia é automaticamente transferida para sua poupança. Round-ups arredondam compras.",
        "benefits": ["Poupa sem esforço", "Consistência > quantidade", "Efeito bola de neve"],
        "features": ["Round-up automático (estilo Acorns)", "Depósitos diários/semanais", "Multiplicador 2x/3x", "Mínimo de R$5 para executar"],
    },
    "regra_10": {
        "name": "Regra 10",
        "origin": "Holanda (Nibud)",
        "icon": "percent",
        "description": "Poupe no mínimo 10% de toda entrada. 85% dos holandeses têm poupança (mediana €20.000).",
        "how_it_works": "10% de cada depósito = automaticamente separado para poupança. Pay yourself first.",
        "benefits": ["Cria reserva automaticamente", "Não depende de sobra no fim do mês", "Mínimo de 10% garantido"],
        "features": ["Percentual configurável", "Auto-depósito no recebimento", "Split automático de paycheck"],
    },
    "lagom": {
        "name": "Gastômetro Lagom",
        "origin": "Suécia (Lagom)",
        "icon": "balance",
        "description": "'Nem demais, nem de menos' — o equilíbrio sueco aplicado aos gastos mensais com burndown chart.",
        "how_it_works": "Gráfico de burndown: gasto projetado vs orçamento. Verde <85%, Amarelo 85-100%, Vermelho >100%.",
        "benefits": ["Evita exageros", "Visualização clara do ritmo", "Compara com média histórica"],
        "features": ["Burndown chart automático", "Comparação com média histórica", "3 zonas de alerta", "Projeção de fim de mês"],
    },
    "desafio_suico": {
        "name": "Desafio Suíço",
        "origin": "Suíça",
        "icon": "shield",
        "description": "Fatura do cartão paga integralmente todo mês. Streak de meses consecutivos sem juros.",
        "how_it_works": "Alertas ao fechar fatura. Meta: pagar 100%. Streak tracking estilo 'duolingo' para motivação.",
        "benefits": ["Zero juros rotativo (média 14% ao mês no BR)", "Disciplina financeira", "Score de crédito limpo"],
        "features": ["Streak de faturas pagas integralmente", "Alerta ao fechar fatura", "Comparação mês a mês", "Cálculo de juros evitados"],
    },
    "acordo_dois": {
        "name": "Acordo a Dois",
        "origin": "Holanda (Polder Model)",
        "icon": "handshake",
        "description": "Consenso financeiro para casais: 3 modelos (conjunto/separado/híbrido). Regras claras de aprovação.",
        "how_it_works": "Escolham o modelo. Definam categorias e limites. Gastos acima do threshold exigem aprovação do parceiro.",
        "benefits": ["Evita brigas por dinheiro", "Transparência total", "Metas conjuntas"],
        "features": ["3 modelos de gestão", "Threshold de aprovação", "Metas compartilhadas", "Notificação ao parceiro"],
    },
    "limpeza_financeira": {
        "name": "Limpeza Financeira",
        "origin": "Suécia (Döstädning)",
        "icon": "broom",
        "description": "Auditoria automática de assinaturas a cada 90 dias. Estilo 'death cleaning' sueco para finanças.",
        "how_it_works": "Detecta assinaturas sem uso nos últimos 90 dias. Mostra quanto você já gastou nelas. Sugere cancelamento.",
        "benefits": ["Elimina gastos esquecidos", "Economia média de 15%", "Mantém só o essencial"],
        "features": ["Detecção de recorrências", "Análise de inatividade (90 dias)", "Cálculo de desperdício total", "Cancelamento 1-clique"],
    },
    "envelope_pix": {
        "name": "Envelopes Pix",
        "origin": "Japão + Brasil",
        "icon": "envelope",
        "description": "Envelopes digitais com saldo por categoria + zero-sum budgeting (cada real tem um trabalho).",
        "how_it_works": "Divida a renda em envelopes. Cada envelope mostra: Orçado, Gasto, Disponível. Saldo não usado = rollover.",
        "benefits": ["Controle total por categoria", "Nunca estoura o orçamento", "Ideal para Pix do dia a dia"],
        "features": ["Zero-sum budgeting (YNAB Rule #1)", "3 estados: Orçado/Gasto/Disponível", "Rollover de saldo não usado", "Alerta ao atingir 80% do envelope"],
    },
}


class MethodsEngine:
    """Engine for global financial methods adapted to Brazil."""

    @staticmethod
    def get_manifest(include_disabled: bool = False) -> dict:
        return METHODS_MANIFEST

    @staticmethod
    def get_method(key: str) -> dict | None:
        return METHODS_MANIFEST.get(key)

    @staticmethod
    async def get_lagom_status(db: AsyncSession, workspace_id: str) -> dict:
        """Calcula o indicador Lagom (verde/amarelo/vermelho) com burndown chart.

        Pesquisa de referência: project burn rate methodology + budget burndown charts.
        """
        today = date.today()
        month_start = today.replace(day=1)
        if month_start.month < 12:
            next_month = month_start.replace(month=month_start.month + 1)
        else:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        days_in_month = (next_month - month_start).days
        day_of_month = today.day

        result = await db.execute(
            select(func.sum(TransactionJournal.amount)).where(
                TransactionJournal.workspace_id == workspace_id,
                TransactionJournal.date.between(month_start, today),
                TransactionJournal.transaction_type == "withdrawal",
            )
        )
        spent_so_far = float(result.scalar() or 0)

        from app.models.budget import BudgetLimit
        budget_result = await db.execute(
            select(func.sum(BudgetLimit.amount)).where(
                BudgetLimit.start_date <= month_start,
                (BudgetLimit.end_date.is_(None) | (BudgetLimit.end_date >= month_start)),
            )
        )
        monthly_budget = float(budget_result.scalar() or 0)

        if monthly_budget == 0:
            avg_result = await db.execute(
                select(func.avg(TransactionJournal.amount)).where(
                    TransactionJournal.workspace_id == workspace_id,
                    TransactionJournal.transaction_type == "withdrawal",
                )
            )
            avg_tx = float(avg_result.scalar() or 0)
            tx_count_result = await db.execute(
                select(func.count(TransactionJournal.id)).where(
                    TransactionJournal.workspace_id == workspace_id,
                    TransactionJournal.transaction_type == "withdrawal",
                    TransactionJournal.date.between(month_start, today),
                )
            )
            tx_count = tx_count_result.scalar() or 1
            monthly_budget = avg_tx * tx_count * 1.5
            using_fallback = True
        else:
            using_fallback = False

        projected = (spent_so_far / day_of_month) * days_in_month if day_of_month > 0 else 0
        ratio = projected / monthly_budget if monthly_budget > 0 else 0
        ideal_burn = monthly_budget / days_in_month
        actual_burn = spent_so_far / day_of_month if day_of_month > 0 else 0

        if ratio < 0.85:
            status = "green"
            message = "Ritmo equilibrado! Gaste projetado dentro do esperado."
        elif ratio < 1.0:
            status = "yellow"
            message = f"Atenção! Projetado: R$ {projected:.0f} de R$ {monthly_budget:.0f}. Reduza o ritmo."
        else:
            status = "red"
            message = f"Crítico! Projetado: R$ {projected:.0f} (orçamento: R$ {monthly_budget:.0f}). Vai estourar!"

        return {
            "status": status,
            "message": message,
            "spent_so_far": round(spent_so_far, 2),
            "monthly_budget": round(monthly_budget, 2),
            "projected": round(projected, 2),
            "remaining": round(max(0, monthly_budget - spent_so_far), 2),
            "day_of_month": day_of_month,
            "days_in_month": days_in_month,
            "ratio": round(ratio, 2),
            "ideal_burn_rate": round(ideal_burn, 2),
            "actual_burn_rate": round(actual_burn, 2),
            "using_estimated_budget": using_fallback,
        }

    @staticmethod
    async def get_swiss_challenge_status(db: AsyncSession, workspace_id: str) -> dict:
        """Desafio Suíço: streak de faturas pagas integralmente, igual Duolingo.

        Pesquisa: Swiss credit card culture - pay in full every month.
        """
        from app.models.credit_card import CreditCardBill
        result = await db.execute(
            select(CreditCardBill).where(
                CreditCardBill.workspace_id == workspace_id,
            ).order_by(CreditCardBill.due_date.desc()).limit(12)
        )
        bills = result.scalars().all()

        if not bills:
            return {"status": "no_data", "message": "Nenhuma fatura encontrada. Ative o Desafio Suíço!"}

        months_checked = []
        full_payment_streak = 0
        total_interest_avoided = 0.0
        for b in bills:
            total = float(b.total_amount or 0)
            paid = float(b.paid_amount or 0)
            paid_full = paid >= total
            months_checked.append({
                "due_date": b.due_date.isoformat(),
                "total": total,
                "paid": paid,
                "paid_full": paid_full,
            })
            if paid_full and b.status == "paid":
                full_payment_streak += 1
            else:
                full_payment_streak = 0
            # Calculate interest avoided (Brazilian avg: 14% monthly revolving credit)
            if paid_full:
                total_interest_avoided += total * 0.14

        return {
            "status": "on_track" if full_payment_streak >= 2 else "warning" if bills else "no_data",
            "message": f"Streak de {full_payment_streak} faturas pagas integralmente!"
                       if full_payment_streak >= 2 else
                       "Pague a próxima fatura integralmente para iniciar seu streak!",
            "full_payment_streak": full_payment_streak,
            "bills_checked": len(bills),
            "total_interest_avoided": round(total_interest_avoided, 2),
            "months": months_checked,
        }

    @staticmethod
    async def run_cleanup_audit(db: AsyncSession, workspace_id: str) -> dict:
        """Limpeza Financeira: detecta assinaturas não usadas nos últimos 90 dias.

        Pesquisa: Rocket Money, Quicken Simplifi, ExpenseBot subscription tracking.
        """
        ninety_days_ago = date.today() - timedelta(days=90)
        six_months_ago = date.today() - timedelta(days=180)

        result = await db.execute(
            select(
                TransactionJournal.description,
                func.sum(TransactionJournal.amount).label("total_spent"),
                func.count(TransactionJournal.id).label("tx_count"),
                func.max(TransactionJournal.date).label("last_used"),
                func.min(TransactionJournal.date).label("first_seen"),
            ).where(
                TransactionJournal.workspace_id == workspace_id,
                TransactionJournal.transaction_type == "withdrawal",
                TransactionJournal.description.isnot(None),
                TransactionJournal.date >= six_months_ago,
            ).group_by(TransactionJournal.description)
            .having(func.count(TransactionJournal.id) >= 3)
            .order_by(func.sum(TransactionJournal.amount).desc())
        )
        subscriptions = []
        for row in result.all():
            last = row.last_used
            if isinstance(last, str):
                from datetime import datetime
                last = datetime.fromisoformat(last).date()
            is_unused = last < ninety_days_ago if last else True
            subscriptions.append({
                "name": row.description,
                "monthly_spent": round(float(row.total_spent or 0) / max(1, row.tx_count), 2),
                "total_spent_6months": round(float(row.total_spent or 0), 2),
                "tx_count": row.tx_count,
                "last_used": last.isoformat() if last else None,
                "is_unused": is_unused,
                "days_since_last_use": (date.today() - last).days if last else None,
            })

        unused = [s for s in subscriptions if s["is_unused"]]
        total_wasted = sum(s["total_spent_6months"] for s in unused)
        monthly_wasted = sum(s["monthly_spent"] for s in unused)

        return {
            "total_subscriptions": len(subscriptions),
            "unused_count": len(unused),
            "total_wasted_6months": round(total_wasted, 2),
            "monthly_wasted": round(monthly_wasted, 2),
            "annual_projection": round(monthly_wasted * 12, 2),
            "subscriptions": subscriptions,
            "unused": unused,
            "suggestion": f"Cancelando {len(unused)} assinatura(s), você economiza R$ {monthly_wasted:.2f}/mês (R$ {monthly_wasted*12:.2f}/ano).",
        }
