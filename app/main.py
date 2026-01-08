import logging
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.settings import settings
from app.api.router import api_router
from app.errors.handlers import register_exception_handlers
from app.middleware.request_id import request_id_middleware
from app.middleware.logging import logging_middleware
from app.middleware.timing import timing_middleware
from app.responses.success import success_response
from app.database import connect_to_database, close_database_connection

from typing import List

logger = logging.getLogger("pennywise")


# Create a logger
logger = logging.getLogger("pennywise")
logger.setLevel(logging.INFO)
# Optionally, you can set up a StreamHandler or FileHandler depending on where you want the logs to go



def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url="/redoc" if settings.ENV != "production" else None,
        openapi_url="/openapi.json" if settings.ENV != "production" else None,
    )

    # -------------------------------------------------
    # Middleware (HTTP-level concerns only)
    # -------------------------------------------------
    app.middleware("http")(request_id_middleware)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(timing_middleware)

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------
    # API Routers
    # -------------------------------------------------
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # -------------------------------------------------
    # Exception Handlers
    # -------------------------------------------------
    register_exception_handlers(app)
    # app.add_exception_handler(RequestValidationError)

    # -------------------------------------------------
    # Application Lifecycle
    # -------------------------------------------------
    @app.on_event("startup")
    async def on_startup():
        try:
            await connect_to_database()
            logger.info("Database connected")
        except Exception as exc:
            logger.critical("Database connection failed", exc_info=exc)
            raise

    @app.on_event("shutdown")
    async def on_shutdown():
        await close_database_connection()
        logger.info("Database connection closed")

    return app


app = create_app()

# -------------------------------------------------
# Health / Root Endpoints
# -------------------------------------------------
health_router = APIRouter(tags=["Health"])


@health_router.get("/")
async def root_health():
    return success_response(
        data={
            "service": "PennyWise API",
            "status": "running",
        }
    )


@health_router.get(settings.API_PREFIX)
async def api_health():
    return success_response(
        data={
            "service": "PennyWise API",
            "api": "ok",
        }
    )

app.include_router(health_router)
