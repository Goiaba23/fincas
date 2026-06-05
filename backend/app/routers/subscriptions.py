from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.users import require_auth
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionAnalytics,
)
from app.services.subscription_service import (
    create_subscription,
    list_subscriptions,
    update_subscription,
    delete_subscription,
    get_analytics,
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["assinaturas"])


@router.post("/", response_model=SubscriptionResponse)
def create(data: SubscriptionCreate, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return create_subscription(db, user.id, data)


@router.get("/", response_model=list[SubscriptionResponse])
def list_all(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return list_subscriptions(db, user.id)


@router.get("/analytics", response_model=SubscriptionAnalytics)
def analytics(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return get_analytics(db, user.id)


@router.put("/{sub_id}", response_model=SubscriptionResponse)
def update(sub_id: str, data: SubscriptionUpdate, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    result = update_subscription(db, sub_id, user.id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return result


@router.delete("/{sub_id}")
def delete(sub_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    if not delete_subscription(db, sub_id, user.id):
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return {"ok": True}
