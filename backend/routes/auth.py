from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from ..auth import create_token, current_user, hash_password, verify_password
from ..database import get_db
from ..models import AuthUser

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=120)
    role: str = Field(default="Worker", pattern="^(Worker|Supervisor|HSE Officer)$")


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    password: str = Field(min_length=8, max_length=120)


class UserResponse(BaseModel):
    username: str
    name: str
    email: str
    role: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.lower().strip()
    email = str(payload.email).lower().strip()
    if db.scalar(select(AuthUser).where(or_(AuthUser.username == username, AuthUser.email == email))):
        raise HTTPException(status_code=409, detail="Username or email is already registered")
    user = AuthUser(username=username, name=payload.name.strip(), email=email, role=payload.role, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_token(user), "user": user}


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identifier = payload.username.lower().strip()
    user = db.scalar(select(AuthUser).where(or_(AuthUser.username == identifier, AuthUser.email == identifier)))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return {"access_token": create_token(user), "user": user}


@router.get("/me", response_model=UserResponse)
def me(user: AuthUser = Depends(current_user)):
    return user
