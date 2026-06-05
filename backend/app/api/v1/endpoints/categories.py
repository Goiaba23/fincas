from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.category import CategoryGroup, Category

router = APIRouter(prefix="/categories", tags=["categories"])


class GroupCreate(BaseModel):
    name: str
    is_income: bool = False
    color: str | None = None
    sort_order: int = 0


class CategoryCreate(BaseModel):
    group_id: str
    name: str
    color: str | None = None
    sort_order: int = 0
    is_hidden: bool = False


# --- Category Groups ---

@router.get("/groups")
async def list_groups(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CategoryGroup).order_by(CategoryGroup.sort_order)
    )
    groups = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "name": g.name,
            "is_income": g.is_income,
            "color": g.color,
            "category_count": len(g.categories) if hasattr(g, 'categories') else 0,
        }
        for g in groups
    ]


@router.post("/groups", status_code=201)
async def create_group(
    req: GroupCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = CategoryGroup(
        name=req.name,
        is_income=req.is_income,
        color=req.color,
        sort_order=req.sort_order,
    )
    db.add(group)
    return {"id": str(group.id), "name": group.name}


# --- Categories ---

@router.get("/")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Category).order_by(Category.sort_order)
    )
    cats = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "group_id": str(c.group_id) if c.group_id else None,
            "color": c.color,
            "is_hidden": c.is_hidden,
        }
        for c in cats
    ]


@router.post("/", status_code=201)
async def create_category(
    req: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cat = Category(
        group_id=req.group_id,
        name=req.name,
        color=req.color,
        sort_order=req.sort_order,
        is_hidden=req.is_hidden,
    )
    db.add(cat)
    return {"id": str(cat.id), "name": cat.name}


@router.get("/{category_id}")
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Category not found")
    return {
        "id": str(cat.id),
        "name": cat.name,
        "group_id": str(cat.group_id),
        "color": cat.color,
        "is_hidden": cat.is_hidden,
    }


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404)
    await db.delete(cat)
