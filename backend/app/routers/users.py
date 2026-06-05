from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, AuthResponse, UserResponse
from app.services.auth import hash_password, verify_password, get_user_by_token

router = APIRouter(prefix="/api/v1/user", tags=["usuarios"])


def require_auth(token: str = Header(...), db: Session = Depends(get_db)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user


@router.post("/register", response_model=AuthResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = None
    if data.phone:
        existing = db.query(User).filter(User.phone == data.phone).first()
    if not existing and data.email:
        existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    user = User(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        token=user.api_token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            phone=user.phone,
            email=user.email,
            avatar=user.avatar,
            login_streak=user.login_streak,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = None
    if data.phone:
        user = db.query(User).filter(User.phone == data.phone).first()
    if not user and data.email:
        user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return AuthResponse(
        token=user.api_token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            phone=user.phone,
            email=user.email,
            avatar=user.avatar,
            login_streak=user.login_streak,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(require_auth)):
    return UserResponse(
        id=user.id,
        name=user.name,
        phone=user.phone,
        email=user.email,
        avatar=user.avatar,
        login_streak=user.login_streak,
        created_at=user.created_at,
    )
