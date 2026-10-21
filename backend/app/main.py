import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppError,
    app_error_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.logging import get_logger, setup_logging

settings = get_settings()
setup_logging(log_level=settings.log_level, app_env=settings.app_env)
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    logger.info(
        "Starting Enterprise RAG Platform API",
        env=settings.app_env,
        version=settings.app_version,
    )
    yield
    logger.info("Shutting down Enterprise RAG Platform API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise-grade Retrieval-Augmented Generation (RAG) platform "
        "featuring hybrid search, fine-grained access control (RBAC), and rigorous evaluation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


class TracingAndLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique X-Request-ID and logs request latency and status."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = request_id

            # Avoid logging raw health check pings excessively at INFO level if desirable, but log access
            logger.info(
                "HTTP request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=process_time_ms,
                request_id=request_id,
            )
            return response
        except Exception:
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "HTTP request failed with unhandled exception",
                method=request.method,
                path=request.url.path,
                duration_ms=process_time_ms,
                request_id=request_id,
            )
            raise


# Add middleware
app.add_middleware(TracingAndLoggingMiddleware)

# Register exception handlers
app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")
