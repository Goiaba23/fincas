from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.users import require_auth
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeResponse,
    ChallengeProgress,
)
from app.services.challenge_service import (
    create_challenge,
    invite_users,
    accept_challenge,
    update_progress,
    list_challenges,
)

router = APIRouter(prefix="/api/v1/challenges", tags=["desafios"])


@router.post("/", response_model=ChallengeResponse)
def create(data: ChallengeCreate, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return create_challenge(db, user.id, data)


@router.post("/invite", response_model=ChallengeResponse)
def invite(challenge_id: str, user_ids: list[str], user: User = Depends(require_auth), db: Session = Depends(get_db)):
    result = invite_users(db, challenge_id, user_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Desafio não encontrado")
    return result


@router.post("/accept/{challenge_id}", response_model=ChallengeResponse)
def accept(challenge_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    result = accept_challenge(db, challenge_id, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Desafio ou convite não encontrado")
    return result


@router.post("/progress/{challenge_id}", response_model=ChallengeResponse)
def progress(challenge_id: str, data: ChallengeProgress, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    result = update_progress(db, challenge_id, user.id, data.progress)
    if not result:
        raise HTTPException(status_code=404, detail="Desafio não encontrado")
    return result


@router.get("/", response_model=list[ChallengeResponse])
def list_all(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return list_challenges(db, user.id)
