from pydantic import BaseModel


class QuestionOption(BaseModel):
    value: str | int
    label: str


class QuizQuestion(BaseModel):
    id: str
    question: str
    type: str
    options: list[QuestionOption] | None = None
    placeholder: str | None = None


class QuizAnswer(BaseModel):
    answers: dict[str, str | int]


class ScoreBreakdown(BaseModel):
    question_id: str
    answer: str | int
    score: int
    weighted: float


class MethodScore(BaseModel):
    key: str
    name: str
    origin: str
    icon: str
    tagline: str
    description: str
    benefits: list[str]
    best_for: str
    score: float
    max_score: float
    percentage: float
    breakdown: list[ScoreBreakdown]


class SaveMethodRequest(BaseModel):
    method_key: str
    method_name: str

class QuizRecommendation(BaseModel):
    top_recommendation: MethodScore | None
    all_scores: list[MethodScore]
    alternatives: list[MethodScore]
    dream_advice: str | None
