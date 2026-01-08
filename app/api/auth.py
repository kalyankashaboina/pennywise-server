from fastapi import APIRouter, Response, Depends, Request, status

from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.security import set_auth_cookies, clear_auth_cookies
from app.dependencies.auth import get_current_user
from app.utils.logger import get_logger

logger = get_logger("pennywise.api.auth")

router = APIRouter()
auth_service = AuthService()


# -------------------------------------------------
# Register
# -------------------------------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request):
    user = await auth_service.register(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        avatar=payload.avatar,
    )

    logger.info(
        "USER_REGISTERED",
        extra={
            "user_id": user.id,
            "email": user.email,
            "ip": request.client.host if request.client else None,
        },
    )

    return {
        "success": True,
        "message": "Registration successful",
        "user_id": user.id,
    }


# -------------------------------------------------
# Login
# -------------------------------------------------
@router.post("/login")
async def login(payload: LoginRequest, response: Response, request: Request):
    access_token, refresh_token = await auth_service.login(
        email=payload.email,
        password=payload.password,
    )

    set_auth_cookies(response, access_token, refresh_token)

    logger.info(
        "USER_LOGIN_SUCCESS",
        extra={
            "email": payload.email,
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )

    return {
        "success": True,
        "message": "Login successful",
    }


# -------------------------------------------------
# Silent refresh (cookie based)
# -------------------------------------------------
@router.post("/refresh")
async def refresh(response: Response, request: Request):
    access_token, refresh_token = await auth_service.refresh_tokens(
        request.cookies
    )

    set_auth_cookies(response, access_token, refresh_token)

    logger.info(
        "TOKEN_REFRESH",
        extra={
            "ip": request.client.host if request.client else None,
        },
    )

    return {
        "success": True,
        "message": "Token refreshed",
    }


# -------------------------------------------------
# Logout
# -------------------------------------------------
@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    current_user=Depends(get_current_user),
):
    clear_auth_cookies(response)
    await auth_service.logout()

    logger.info(
        "USER_LOGOUT",
        extra={
            "user_id": current_user.id,
            "ip": request.client.host if request.client else None,
        },
    )

    return {
        "success": True,
        "message": "Logout successful",
    }


# -------------------------------------------------
# Forgot password
# -------------------------------------------------
@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, request: Request):
    await auth_service.request_password_reset(payload.email)

    logger.info(
        "PASSWORD_RESET_REQUEST",
        extra={
            "email": payload.email,
            "ip": request.client.host if request.client else None,
        },
    )

    # Always return success (anti-enumeration)
    return {
        "success": True,
        "message": "If the email exists, a reset link was sent",
    }


# -------------------------------------------------
# Reset password
# -------------------------------------------------
@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, request: Request):
    await auth_service.reset_password(
        token=payload.token,
        new_password=payload.new_password,
    )

    logger.info(
        "PASSWORD_RESET_SUCCESS",
        extra={
            "ip": request.client.host if request.client else None,
        },
    )

    return {
        "success": True,
        "message": "Password reset successful",
    }


