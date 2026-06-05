from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import Subscription
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionAnalytics,
)


def _to_response(sub: Subscription) -> SubscriptionResponse:
    monthly = sub.amount
    if sub.billing_cycle == "yearly":
        monthly = sub.amount / 12
    elif sub.billing_cycle == "quarterly":
        monthly = sub.amount / 3
    elif sub.billing_cycle == "weekly":
        monthly = sub.amount * 4.33
    return SubscriptionResponse(
        id=sub.id,
        name=sub.name,
        amount=sub.amount,
        billing_cycle=sub.billing_cycle,
        category=sub.category,
        next_payment=sub.next_payment,
        active=sub.active,
        monthly_cost=round(monthly, 2),
    )


def create_subscription(db: Session, user_id: str, data: SubscriptionCreate):
    sub = Subscription(
        user_id=user_id,
        name=data.name,
        amount=data.amount,
        billing_cycle=data.billing_cycle,
        category=data.category,
        next_payment=datetime.fromisoformat(data.next_payment) if data.next_payment else None,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return _to_response(sub)


def list_subscriptions(db: Session, user_id: str):
    subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    return [_to_response(s) for s in subs]


def update_subscription(db: Session, sub_id: str, user_id: str, data: SubscriptionUpdate):
    sub = db.query(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == user_id).first()
    if not sub:
        return None
    if data.name is not None:
        sub.name = data.name
    if data.amount is not None:
        sub.amount = data.amount
    if data.billing_cycle is not None:
        sub.billing_cycle = data.billing_cycle
    if data.category is not None:
        sub.category = data.category
    if data.next_payment is not None:
        sub.next_payment = datetime.fromisoformat(data.next_payment) if data.next_payment else None
    if data.active is not None:
        sub.active = data.active
    db.commit()
    db.refresh(sub)
    return _to_response(sub)


def delete_subscription(db: Session, sub_id: str, user_id: str):
    sub = db.query(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == user_id).first()
    if not sub:
        return False
    db.delete(sub)
    db.commit()
    return True


def get_analytics(db: Session, user_id: str):
    subs = db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.active == True).all()
    total_monthly = 0
    by_category = {}
    for s in subs:
        monthly = s.amount
        if s.billing_cycle == "yearly":
            monthly = s.amount / 12
        elif s.billing_cycle == "quarterly":
            monthly = s.amount / 3
        elif s.billing_cycle == "weekly":
            monthly = s.amount * 4.33
        total_monthly += monthly
        by_category[s.category] = by_category.get(s.category, 0) + monthly

    top = sorted(
        [{"name": s.name, "monthly_cost": round(monthly, 2)} for s in subs],
        key=lambda x: x["monthly_cost"],
        reverse=True,
    )[:5]

    return SubscriptionAnalytics(
        total_monthly=round(total_monthly, 2),
        total_yearly=round(total_monthly * 12, 2),
        subscription_count=len(subs),
        by_category={k: round(v, 2) for k, v in by_category.items()},
        top_spending=top,
    )
