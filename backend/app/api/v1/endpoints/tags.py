from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.tag import Tag

router = APIRouter(prefix="/tags", tags=["tags"])


class TagCreate(BaseModel):
    name: str
    color: str | None = None


@router.get("/")
async def list_tags(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Tag).order_by(Tag.name)
    )
    tags = result.scalars().all()
    return [
        {"id": str(t.id), "name": t.name, "color": t.color}
        for t in tags
    ]


@router.post("/", status_code=201)
async def create_tag(
    req: TagCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tag = Tag(name=req.name, color=req.color)
    db.add(tag)
    return {"id": str(tag.id), "name": tag.name}


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(404)
    await db.delete(tag)
