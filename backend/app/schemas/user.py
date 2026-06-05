from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str = Field(min_length=4)


class UserLogin(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    avatar: str
    login_streak: int
    created_at: datetime


class AuthResponse(BaseModel):
    token: str
    user: UserResponse
