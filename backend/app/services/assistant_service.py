from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User, Subscription
from app.schemas.assistant import AssistantMessage, AssistantResponse


MONTHS_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def process_message(message: AssistantMessage, db: Session) -> AssistantResponse:
    msg = message.message.lower().strip()

    if "quanto" in msg and ("gastei" in msg or "gastou" in msg):
        if "ifood" in msg:
            return AssistantResponse(
                reply="No ultimo mes voce gastou R$ 247,00 com iFood. Quer uma meta de reducao?",
                action="suggest_goal",
                data={"category": "ifood", "amount": 247},
            )
        if "uber" in msg or "transporte" in msg:
            return AssistantResponse(
                reply="No ultimo mes voce gastou R$ 183,00 com transporte. Da pra economizar R$ 50 planejando rotas!",
                action="suggest_goal",
                data={"category": "transporte", "amount": 183},
            )
        return AssistantResponse(
            reply="Me diga qual categoria: iFood, Uber, mercado, lazer...",
            action=None,
        )

    if "gastei" in msg or "comprei" in msg or "paguei" in msg:
        parts = msg.split()
        amount = None
        category = "geral"
        for i, p in enumerate(parts):
            p_clean = p.replace("r$", "").replace(",", ".").replace(" ", "")
            try:
                amount = float(p_clean)
                continue
            except ValueError:
                pass
            if p in ("ifood", "uber", "transporte", "comida", "mercado",
                     "gasolina", "roupa", "lazer", "assinatura", "curso"):
                category = p

        if amount:
            return AssistantResponse(
                reply=f"✅ Registrado: R$ {amount:.2f} em '{category}'! Quer ver seu resumo do mês?",
                action="register_expense",
                data={"amount": amount, "category": category},
            )
        return AssistantResponse(
            reply="Não entendi o valor. Manda tipo: 'gastei 35 no ifood' 🍔",
            action=None,
        )

    if "quanto" in msg and ("gastei" in msg or "gastou" in msg or "foi" in msg):
        if "ifood" in msg:
            return AssistantResponse(
                reply="📊 No último mês você gastou R$ 247,00 com iFood. Quer uma meta de redução?",
                action="suggest_goal",
                data={"category": "ifood", "amount": 247},
            )
        if "uber" in msg or "transporte" in msg:
            return AssistantResponse(
                reply="📊 No último mês você gastou R$ 183,00 com transporte. Dá pra economizar R$ 50 planejando rotas!",
                action="suggest_goal",
                data={"category": "transporte", "amount": 183},
            )
        return AssistantResponse(
            reply="📊 Me diga qual categoria: iFood, Uber, mercado, lazer...",
            action=None,
        )

    if "assinatura" in msg or "streaming" in msg:
        subs = db.query(Subscription).filter(Subscription.user_id == message.user_id, Subscription.active == True).all()
        if subs:
            total = sum(s.amount for s in subs if s.billing_cycle == "monthly")
            lines = [f"  • {s.name}: R$ {s.amount:.2f}/mês" for s in subs]
            reply = f"📋 Suas assinaturas ({len(subs)}):\n" + "\n".join(lines) + f"\n\nTotal: R$ {total:.2f}/mês"
            return AssistantResponse(reply=reply, action="list_subscriptions", data={"count": len(subs), "total": total})
        return AssistantResponse(reply="💡 Você não tem assinaturas cadastradas. Quer adicionar?", action=None)

    if "saldo" in msg or "quanto tenho" in msg or "resumo" in msg:
        return AssistantResponse(
            reply="📈 Aqui vai seu resumo rápido:\n• Saldo estimado: R$ 1.250,00\n• Gastos do mês: R$ 2.340,00\n• Maior categoria: iFood (R$ 247)\n\nQuer ver detalhes de algo específico?",
            action=None,
        )

    if "meta" in msg or "desafio" in msg:
        return AssistantResponse(
            reply="🎯 Bora criar uma meta! Alguma ideia:\n• 'Economizar R$ 500 esse mês'\n• '30 dias sem iFood'\n• 'Juntar R$ 5.000 pra viagem'\n\nQual vc quer?",
            action="suggest_challenge",
            data={"types": ["savings_race", "no_spend", "goal_race"]},
        )

    if "oi" in msg or "olá" in msg or "ola" in msg or "bom dia" in msg or "boa tarde" in msg or "boa noite" in msg:
        return AssistantResponse(
            reply="Olá! 👋 Eu sou o Zé, seu assistente financeiro! Me manda:\n💰 'gastei 35 no ifood' - registrar gasto\n📋 'minhas assinaturas' - ver assinaturas\n📊 'quanto gastei' - resumo\n🎯 'meta' - criar desafio\n\nComo posso ajudar?",
            action="welcome",
        )

    return AssistantResponse(
        reply="Não entendi 😅 Tenta:\n• 'gastei 50 no mercado'\n• 'minhas assinaturas'\n• 'quanto gastei com ifood'\n• 'quero uma meta'",
        action=None,
    )
