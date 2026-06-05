from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user import User, Subscription
from app.schemas.score import ScoreResponse, ScoreFactor, DailyCheckinResponse


def calculate_score(db: Session, user: User):
    factors = []
    tips = []

    checkin_score = min(user.login_streak * 5, 100)
    factors.append(ScoreFactor(
        name="checkin",
        value=checkin_score,
        max_value=100,
        weight=0.20,
        description="Consistência de login diário"
    ))
    if user.login_streak < 7:
        tips.append("Faça check-in por 7 dias seguidos pra ganhar bônus de consistência")

    sub_count = db.query(Subscription).filter(Subscription.user_id == user.id).count()
    tracking_score = min(sub_count * 10, 100)
    factors.append(ScoreFactor(
        name="assinaturas",
        value=tracking_score,
        max_value=100,
        weight=0.15,
        description="Quantas assinaturas você cadastrou"
    ))
    if sub_count < 2:
        tips.append("Cadastre suas assinaturas pra saber quanto gasta por mês")

    total_checked = min(user.total_checked_days * 2, 100)
    factors.append(ScoreFactor(
        name="engajamento",
        value=total_checked,
        max_value=100,
        weight=0.25,
        description="Dias totais de uso do app"
    ))
    if user.total_checked_days < 15:
        tips.append("Use o app por 15 dias pra desbloquear o relatório financeiro completo")

    if user.login_streak >= 30:
        streak_bonus = 100
        tips.append("🔥 Streak de 30 dias! Você é um mestre das finanças!")
    elif user.login_streak >= 14:
        streak_bonus = 60
        tips.append("🌟 14 dias de streak! Continue assim!")
    elif user.login_streak >= 7:
        streak_bonus = 30
        tips.append("⭐ 7 dias de streak! Já é um hábito!")
    else:
        streak_bonus = 0

    factors.append(ScoreFactor(
        name="streak_bonus",
        value=streak_bonus,
        max_value=100,
        weight=0.15,
        description=f"Bônus por streak de {user.login_streak} dias"
    ))

    base = (
        factors[0].value * factors[0].weight
        + factors[1].value * factors[1].weight
        + factors[2].value * factors[2].weight
        + factors[3].value * factors[3].weight
    )
    raw_score = int(base)
    max_score = 100

    if raw_score >= 80:
        level = "Mestre Financeiro 👑"
    elif raw_score >= 60:
        level = "Investidor em Ascensão 📈"
    elif raw_score >= 40:
        level = "Aprendiz Disciplinado 📚"
    elif raw_score >= 20:
        level = "Iniciante Curioso 🌱"
    else:
        level = "Descobridor 💎"

    return ScoreResponse(
        score=raw_score,
        max_score=max_score,
        level=level,
        factors=factors,
        tips=tips,
    )


def daily_checkin(db: Session, user: User):
    today = datetime.utcnow().date()
    last = user.last_login_date.date() if user.last_login_date else None

    if last == today:
        return DailyCheckinResponse(
            message="Check-in de hoje já foi feito! Volte amanhã 🔄",
            streak=user.login_streak,
            bonus=0,
        )

    yesterday = today - timedelta(days=1)
    if last == yesterday or last is None:
        user.login_streak += 1
    else:
        user.login_streak = 1

    user.last_login_date = datetime.utcnow()
    user.total_checked_days += 1
    db.commit()

    bonus = 0
    if user.login_streak == 7:
        bonus = 50
    elif user.login_streak == 14:
        bonus = 100
    elif user.login_streak == 30:
        bonus = 300
    elif user.login_streak == 90:
        bonus = 1000
    elif user.login_streak == 365:
        bonus = 5000

    msg = f"Check-in feito! 🔥 Streak de {user.login_streak} dias"
    if bonus:
        msg += f" | Bônus de {bonus} pontos! 🎉"

    return DailyCheckinResponse(message=msg, streak=user.login_streak, bonus=bonus)
