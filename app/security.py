from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets

from fastapi import Response
from jose import jwt
from passlib.context import CryptContext

from app.settings import settings


# -------------------------------------------------
# Password hashing (bcrypt-safe, production-grade)
# -------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def _prehash(password: str) -> str:
    """
    Pre-hash password using SHA-256 to avoid bcrypt 72-byte limit.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate the plain_password to 72 bytes
    plain_password = plain_password[:72]
    return pwd_context.verify(_prehash(plain_password), hashed_password)

# -------------------------------------------------
# JWT handling
# -------------------------------------------------

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# -------------------------------------------------
# Password reset helpers
# -------------------------------------------------

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# -------------------------------------------------
# Auth cookies
# -------------------------------------------------

def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=15 * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
