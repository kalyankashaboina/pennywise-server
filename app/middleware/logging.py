from fastapi import Request

from app.utils.logger import get_logger

logger = get_logger("pennywise")


async def logging_middleware(request: Request, call_next):
    logger.info(f"HTTP {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"HTTP {request.method} {request.url.path} -> {response.status_code}")
    return response
