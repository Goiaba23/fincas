from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.users import require_auth
from app.schemas.gastronomy import (
    GastronomyPostCreate,
    GastronomyPostUpdate,
    GastronomyPostResponse,
)
from app.services.gastronomy_service import (
    create_post,
    list_posts,
    get_post,
    update_post,
    delete_post,
)

router = APIRouter(prefix="/api/v1/gastronomy", tags=["gastronomia"])


@router.get("/", response_model=list[GastronomyPostResponse])
def list_all(category: str = None, featured: bool = None, db: Session = Depends(get_db)):
    return list_posts(db, category, featured)


@router.get("/{post_id}", response_model=GastronomyPostResponse)
def get_one(post_id: str, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")
    return post


@router.post("/", response_model=GastronomyPostResponse)
def create(data: GastronomyPostCreate, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    return create_post(db, data)


@router.put("/{post_id}", response_model=GastronomyPostResponse)
def update(post_id: str, data: GastronomyPostUpdate, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    post = update_post(db, post_id, data)
    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")
    return post


@router.delete("/{post_id}")
def delete(post_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    if not delete_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post nao encontrado")
    return {"ok": True}
