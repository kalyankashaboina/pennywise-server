from fastapi import Request
from jose import JWTError, jwt

from app.settings import settings
from app.errors.base import AppError
from app.errors.codes import ErrorCode
from app.repositories.user_repo import UserRepository
from app.utils.logger import get_logger

logger = get_logger("pennywise.auth")
user_repo = UserRepository()


async def get_current_user(request: Request):
    """
    Extract authenticated user from access_token cookie.
    """

    token = request.cookies.get("access_token")
    if not token:
        logger.warning("Access denied: missing access_token cookie")
        raise AppError(
            code=ErrorCode.UNAUTHORIZED,
            message="Not authenticated",
            status_code=401,
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError("Missing subject")
    except JWTError as e:
        logger.warning(f"Access denied: JWT error | reason={str(e)}")
        raise AppError(
            code=ErrorCode.UNAUTHORIZED,
            message="Invalid or expired token",
            status_code=401,
        )

    user = await user_repo.get_by_id(user_id)
    if not user:
        logger.warning(f"Access denied: user not found | user_id={user_id}")
        raise AppError(
            code=ErrorCode.UNAUTHORIZED,
            message="User not found",
            status_code=401,
        )

    logger.debug(f"Authenticated request | user_id={user.id}")
    return user
