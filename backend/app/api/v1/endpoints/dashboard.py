from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/api/v1/dashboard")
async def get_dashboard(
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db, str(workspace.id))
    return await service.get_full_dashboard()
