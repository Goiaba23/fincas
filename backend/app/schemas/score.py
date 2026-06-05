from pydantic import BaseModel


class ScoreFactor(BaseModel):
    name: str
    value: float
    max_value: float
    weight: float
    description: str


class ScoreResponse(BaseModel):
    score: int
    max_score: int
    level: str
    factors: list[ScoreFactor]
    tips: list[str]


class DailyCheckinResponse(BaseModel):
    message: str
    streak: int
    bonus: int
