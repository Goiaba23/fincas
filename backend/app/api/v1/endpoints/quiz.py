from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMethod
from app.schemas.quiz import QuizAnswer, QuizRecommendation, SaveMethodRequest
from app.services.quiz_service import QUIZ_QUESTIONS, get_recommendation

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/questions")
async def list_questions(user: User = Depends(get_current_user)):
    return QUIZ_QUESTIONS


@router.post("/recommend", response_model=QuizRecommendation)
async def recommend_method(
    req: QuizAnswer,
    user: User = Depends(get_current_user),
):
    return get_recommendation(req.answers)


@router.post("/save-recommendation")
async def save_recommendation(
    req: SaveMethodRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.get(WorkspaceMethod, (str(workspace.id), req.method_key))
    if existing:
        existing.is_enabled = True
    else:
        db.add(WorkspaceMethod(workspace_id=str(workspace.id), method=req.method_key, is_enabled=True))
    await db.commit()
    return {"status": "ok", "method": req.method_key}
