from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
ALGORITHM = "HS256"


class TokenDecodeError(Exception):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except PyJWTError as exc:
        raise TokenDecodeError("Invalid token") from exc
