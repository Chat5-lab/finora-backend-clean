from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.hash import bcrypt
from pydantic import BaseModel
from settings import settings

ALGO = "HS256"
ACCESS_TTL_MIN = int(getattr(settings, "ACCESS_TOKEN_EXPIRE_MIN", 30))
REFRESH_TTL_MIN = int(getattr(settings, "REFRESH_TOKEN_EXPIRE_MIN", 43200))  # 30 days

def get_password_hash(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.verify(pw, hashed)

def _create(sub: str, minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=minutes)).timestamp())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGO)

def create_access_token(sub: str) -> str:
    return _create(sub, ACCESS_TTL_MIN)

def create_refresh_token(sub: str) -> str:
    return _create(sub, REFRESH_TTL_MIN)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
