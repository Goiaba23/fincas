from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChallengeCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    challenge_type: str = Field(pattern="^(savings_race|no_spend|goal_race|streak)$")
    goal_value: float = Field(default=0, ge=0)
    category_filter: Optional[str] = None
    end_date: str


class ChallengeInvite(BaseModel):
    challenge_id: str
    user_ids: list[str]


class ChallengeProgress(BaseModel):
    progress: float = Field(ge=0)
    note: Optional[str] = None


class ParticipantResponse(BaseModel):
    user_id: str
    user_name: str
    avatar: str
    progress: float
    accepted: bool


class ChallengeResponse(BaseModel):
    id: str
    title: str
    challenge_type: str
    goal_value: float
    category_filter: Optional[str]
    creator_id: str
    start_date: datetime
    end_date: datetime
    active: bool
    participants: list[ParticipantResponse]
