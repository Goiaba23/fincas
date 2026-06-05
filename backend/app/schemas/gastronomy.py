from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GastronomyPostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    summary: str = Field(min_length=10, max_length=500)
    content: Optional[str] = None
    category: str = Field(pattern="^(novidade|promocao|evento|review|dica)$")
    image_url: Optional[str] = None
    blog_url: Optional[str] = None
    author: Optional[str] = None
    featured: bool = False


class GastronomyPostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    blog_url: Optional[str] = None
    author: Optional[str] = None
    published: Optional[bool] = None
    featured: Optional[bool] = None


class GastronomyPostResponse(BaseModel):
    id: str
    title: str
    summary: str
    content: Optional[str]
    category: str
    image_url: Optional[str]
    blog_url: Optional[str]
    author: str
    featured: bool
    created_at: datetime
