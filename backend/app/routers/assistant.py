from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.users import require_auth
from app.schemas.assistant import AssistantMessage, AssistantResponse
from app.services.assistant_service import process_message

router = APIRouter(prefix="/api/v1/assistant", tags=["assistente"])


@router.post("/chat", response_model=AssistantResponse)
def chat(data: AssistantMessage, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return process_message(data, db)
