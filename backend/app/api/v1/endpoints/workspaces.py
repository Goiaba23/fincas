from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class WorkspaceCreate(BaseModel):
    name: str
    kind: str = "personal"
    default_currency: str = "BRL"


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    kind: str | None = None
    default_currency: str | None = None
    icon: str | None = None
    color: str | None = None


class AddMemberRequest(BaseModel):
    email: str
    role: str = "editor"


@router.get("/")
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember)
        .where(WorkspaceMember.user_id == user.id)
    )
    workspaces = result.scalars().all()
    return [
        {
            "id": str(w.id),
            "name": w.name,
            "kind": w.kind,
            "currency": w.default_currency,
            "is_archived": w.is_archived,
        }
        for w in workspaces
    ]


@router.post("/", status_code=201)
async def create_workspace(
    req: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ws = Workspace(
        name=req.name,
        kind=req.kind,
        default_currency=req.default_currency,
        created_by=user.id,
    )
    db.add(ws)
    await db.flush()

    member = WorkspaceMember(
        workspace_id=ws.id,
        user_id=user.id,
        role="owner",
    )
    db.add(member)

    return {
        "id": str(ws.id),
        "name": ws.name,
        "kind": ws.kind,
        "role": "owner",
    }


@router.get("/{workspace_id}")
async def get_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.is_archived == False,
        )
    )
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "Workspace not found")

    members_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.workspace_id == ws.id)
    )
    members = members_result.scalars().all()

    return {
        "id": str(ws.id),
        "name": ws.name,
        "kind": ws.kind,
        "currency": ws.default_currency,
        "icon": ws.icon,
        "color": ws.color,
        "members": [
            {"user_id": str(m.user_id), "role": m.role} for m in members
        ],
    }


@router.patch("/{workspace_id}")
async def update_workspace(
    workspace_id: UUID,
    req: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404)

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ws, key, value)

    return {"id": str(ws.id), "name": ws.name}


@router.delete("/{workspace_id}", status_code=204)
async def archive_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404)

    ws.is_archived = True


@router.post("/{workspace_id}/members")
async def add_member(
    workspace_id: UUID,
    req: AddMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.role == "owner",
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(403, "Only owners can add members")

    user_result = await db.execute(
        select(User).where(User.email == req.email)
    )
    invited = user_result.scalar_one_or_none()
    if not invited:
        raise HTTPException(404, "User not found")

    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=invited.id,
        role=req.role,
        invited_by=current_user.id,
    )
    db.add(member)

    return {"user_id": str(invited.id), "role": req.role}
