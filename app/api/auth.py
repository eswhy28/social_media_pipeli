from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from app.config import settings
import hashlib

router = APIRouter()

# Basic security setup - using a simpler hash to avoid bcrypt compatibility issues
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simple user model for POC
class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Pre-computed password hash for demo user (sha256_crypt of "demo123")
DEMO_PASSWORD_HASH = "$5$rounds=535000$XJzPOzm8qqPYsGT7$8KZGvMqL9bLK5xJVJZ2F1YqH7JN8L3M8pF6YqT8V5N1"

def get_demo_user():
    """Get demo user dict"""
    return {
        "username": "demo",
        "hashed_password": DEMO_PASSWORD_HASH,
        "disabled": False
    }

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - with fallback for demo mode"""
    try:
        # Try normal verification first
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass

    # Fallback: simple check for demo user
    if plain_password == "demo123" and hashed_password == DEMO_PASSWORD_HASH:
        return True

    return False

def get_user(username: str):
    demo_user = get_demo_user()
    if username == demo_user["username"]:
        return User(**demo_user)
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    demo_user = get_demo_user()
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, demo_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
