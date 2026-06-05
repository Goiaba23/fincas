from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.users import require_auth
from app.schemas.score import ScoreResponse, DailyCheckinResponse
from app.services.score_service import calculate_score, daily_checkin

router = APIRouter(prefix="/api/v1/score", tags=["score"])


@router.get("/", response_model=ScoreResponse)
def get_score(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return calculate_score(db, user)


@router.post("/checkin", response_model=DailyCheckinResponse)
def checkin(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return daily_checkin(db, user)
