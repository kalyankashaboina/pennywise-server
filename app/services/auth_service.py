from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.errors.base import AppError
from app.errors.codes import ErrorCode
from app.repositories.user_repo import UserRepository
from app.security import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.services.audit_service import AuditService
from app.settings import settings
from app.utils.logger import get_logger

logger = get_logger("pennywise.auth")


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.audit = AuditService()

    # -------------------------------------------------
    # Register
    # -------------------------------------------------
    async def register(
        self,
        *,
        email: str,
        username: str,
        password: str,
        avatar: Optional[str] = None,
        request=None,
    ):
        logger.info("Register attempt", extra={"email": email, "username": username})

        if await self.user_repo.get_by_email(email):
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Email already in use",
                status_code=400,
            )

        if await self.user_repo.get_by_username(username):
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Username already in use",
                status_code=400,
            )

        user = await self.user_repo.create(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            avatar=avatar,
        )

        await self.audit.log(
            action="USER_REGISTERED",
            user_id=user.id,
            entity="user",
            entity_id=user.id,
            request=request,
        )

        logger.info("User registered", extra={"user_id": user.id})
        return user

    # -------------------------------------------------
    # Login
    # -------------------------------------------------
    async def login(self, *, email: str, password: str, request=None):
        logger.info("Login attempt", extra={"email": email})

        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            await self.audit.log(
                action="LOGIN_FAILED",
                user_id=None,
                metadata={"email": email},
                request=request,
            )
            raise AppError(
                code=ErrorCode.UNAUTHORIZED,
                message="Invalid credentials",
                status_code=401,
            )

        access = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=60),
        )
        refresh = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(days=30),
        )

        await self.audit.log(
            action="LOGIN_SUCCESS",
            user_id=user.id,
            entity="user",
            entity_id=user.id,
            request=request,
        )

        logger.info("Login success", extra={"user_id": user.id})
        return access, refresh

    # -------------------------------------------------
    # Refresh tokens
    # -------------------------------------------------
    async def refresh_tokens(self, *, cookies: dict, request=None):
        refresh_token = cookies.get("refresh_token")
        if not refresh_token:
            raise AppError(
                code=ErrorCode.UNAUTHORIZED,
                message="Missing refresh token",
                status_code=401,
            )

        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            user_id = payload.get("sub")
            if not user_id:
                raise JWTError()
        except JWTError as e:
            raise AppError(
                code=ErrorCode.UNAUTHORIZED,
                message="Invalid refresh token",
                status_code=401,
            ) from e

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AppError(
                code=ErrorCode.UNAUTHORIZED,
                message="User not found",
                status_code=401,
            )

        access = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=15),
        )
        refresh = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(days=30),
        )

        await self.audit.log(
            action="TOKEN_REFRESH",
            user_id=user.id,
            entity="user",
            entity_id=user.id,
            request=request,
        )

        return access, refresh

    # -------------------------------------------------
    # Forgot password
    # -------------------------------------------------
    async def request_password_reset(self, *, email: str, request=None):
        user = await self.user_repo.get_by_email(email)

        # Always silent
        if not user:
            await self.audit.log(
                action="PASSWORD_RESET_REQUEST_UNKNOWN_EMAIL",
                user_id=None,
                metadata={"email": email},
                request=request,
            )
            return None

        token = generate_reset_token()

        await self.user_repo.set_reset_token(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        )

        await self.audit.log(
            action="PASSWORD_RESET_REQUESTED",
            user_id=user.id,
            entity="user",
            entity_id=user.id,
            request=request,
        )

        return token  # dev only

    # -------------------------------------------------
    # Reset password
    # -------------------------------------------------
    async def reset_password(self, *, token: str, new_password: str, request=None):
        user = await self.user_repo.get_by_reset_token(hash_token(token))
        if not user:
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Invalid or expired reset token",
                status_code=400,
            )

        await self.user_repo.update_password(
            user_id=user.id,
            hashed_password=hash_password(new_password),
        )

        await self.audit.log(
            action="PASSWORD_RESET_SUCCESS",
            user_id=user.id,
            entity="user",
            entity_id=user.id,
            request=request,
        )

    # -------------------------------------------------
    # Logout
    # -------------------------------------------------
    async def logout(self, *, user_id: Optional[str], request=None):
        """
        Stateless logout.
        Cookies are cleared at API layer.
        Audit still matters.
        """
        await self.audit.log(
            action="LOGOUT",
            user_id=user_id,
            entity="user",
            entity_id=user_id,
            request=request,
        )

        logger.info("Logout completed", extra={"user_id": user_id})
