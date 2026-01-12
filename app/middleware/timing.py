import time

from fastapi import Request
from fastapi.responses import Response


async def timing_middleware(request: Request, call_next) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    return response
