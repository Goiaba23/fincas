from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import Challenge, ChallengeParticipant, User
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeResponse,
    ParticipantResponse,
)


def create_challenge(db: Session, creator_id: str, data: ChallengeCreate):
    challenge = Challenge(
        creator_id=creator_id,
        title=data.title,
        challenge_type=data.challenge_type,
        goal_value=data.goal_value,
        category_filter=data.category_filter,
        end_date=datetime.fromisoformat(data.end_date),
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    participant = ChallengeParticipant(
        challenge_id=challenge.id,
        user_id=creator_id,
        accepted=True,
    )
    db.add(participant)
    db.commit()

    return _to_response(db, challenge)


def invite_users(db: Session, challenge_id: str, user_ids: list[str]):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        return None

    for uid in user_ids:
        existing = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == uid,
        ).first()
        if not existing:
            p = ChallengeParticipant(challenge_id=challenge_id, user_id=uid)
            db.add(p)
    db.commit()
    return _to_response(db, challenge)


def accept_challenge(db: Session, challenge_id: str, user_id: str):
    p = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.challenge_id == challenge_id,
        ChallengeParticipant.user_id == user_id,
    ).first()
    if not p:
        return None
    p.accepted = True
    db.commit()
    return _to_response(db, db.query(Challenge).filter(Challenge.id == challenge_id).first())


def update_progress(db: Session, challenge_id: str, user_id: str, progress: float):
    p = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.challenge_id == challenge_id,
        ChallengeParticipant.user_id == user_id,
    ).first()
    if not p:
        return None
    p.progress = progress
    db.commit()
    return _to_response(db, db.query(Challenge).filter(Challenge.id == challenge_id).first())


def list_challenges(db: Session, user_id: str):
    participations = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == user_id
    ).all()
    challenge_ids = [p.challenge_id for p in participations]
    challenges = db.query(Challenge).filter(Challenge.id.in_(challenge_ids)).all()
    return [_to_response(db, c) for c in challenges]


def _to_response(db: Session, challenge: Challenge) -> ChallengeResponse:
    participants = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.challenge_id == challenge.id
    ).all()

    p_responses = []
    for p in participants:
        user = db.query(User).filter(User.id == p.user_id).first()
        p_responses.append(ParticipantResponse(
            user_id=p.user_id,
            user_name=user.name if user else "?",
            avatar=user.avatar if user else "?",
            progress=p.progress,
            accepted=p.accepted,
        ))

    return ChallengeResponse(
        id=challenge.id,
        title=challenge.title,
        challenge_type=challenge.challenge_type,
        goal_value=challenge.goal_value,
        category_filter=challenge.category_filter,
        creator_id=challenge.creator_id,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        active=challenge.active,
        participants=p_responses,
    )
