from sqlalchemy.orm import Session

from app.models.user import GastronomyPost
from app.schemas.gastronomy import (
    GastronomyPostCreate,
    GastronomyPostUpdate,
    GastronomyPostResponse,
)


def _to_response(post: GastronomyPost) -> GastronomyPostResponse:
    return GastronomyPostResponse(
        id=post.id,
        title=post.title,
        summary=post.summary,
        content=post.content,
        category=post.category,
        image_url=post.image_url,
        blog_url=post.blog_url,
        author=post.author,
        featured=post.featured,
        created_at=post.created_at,
    )


def create_post(db: Session, data: GastronomyPostCreate):
    post = GastronomyPost(
        title=data.title,
        summary=data.summary,
        content=data.content,
        category=data.category,
        image_url=data.image_url,
        blog_url=data.blog_url,
        author=data.author or "Equipe Financa Jovem",
        featured=data.featured,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _to_response(post)


def list_posts(db: Session, category: str = None, featured: bool = None):
    query = db.query(GastronomyPost).filter(GastronomyPost.published == True)
    if category:
        query = query.filter(GastronomyPost.category == category)
    if featured:
        query = query.filter(GastronomyPost.featured == True)
    posts = query.order_by(GastronomyPost.created_at.desc()).all()
    return [_to_response(p) for p in posts]


def get_post(db: Session, post_id: str):
    post = db.query(GastronomyPost).filter(GastronomyPost.id == post_id).first()
    return _to_response(post) if post else None


def update_post(db: Session, post_id: str, data: GastronomyPostUpdate):
    post = db.query(GastronomyPost).filter(GastronomyPost.id == post_id).first()
    if not post:
        return None
    if data.title is not None:
        post.title = data.title
    if data.summary is not None:
        post.summary = data.summary
    if data.content is not None:
        post.content = data.content
    if data.category is not None:
        post.category = data.category
    if data.image_url is not None:
        post.image_url = data.image_url
    if data.blog_url is not None:
        post.blog_url = data.blog_url
    if data.author is not None:
        post.author = data.author
    if data.published is not None:
        post.published = data.published
    if data.featured is not None:
        post.featured = data.featured
    db.commit()
    db.refresh(post)
    return _to_response(post)


def delete_post(db: Session, post_id: str):
    post = db.query(GastronomyPost).filter(GastronomyPost.id == post_id).first()
    if not post:
        return False
    db.delete(post)
    db.commit()
    return True
