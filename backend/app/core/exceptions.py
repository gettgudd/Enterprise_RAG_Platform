from typing import Any
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger(__name__)


class AppError(Exception):
    """Base application exception for Enterprise RAG Platform."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class DocumentNotFoundError(AppError):
    def __init__(self, document_id: str, message: str | None = None) -> None:
        super().__init__(
            message=message or f"Document '{document_id}' was not found.",
            code="DOCUMENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"document_id": document_id},
        )


class PermissionDeniedError(AppError):
    def __init__(self, resource: str, action: str = "read", message: str | None = None) -> None:
        super().__init__(
            message=message or f"Permission denied for action '{action}' on resource '{resource}'.",
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"resource": resource, "action": action},
        )


class DependencyUnavailableError(AppError):
    def __init__(self, dependency: str, message: str | None = None) -> None:
        super().__init__(
            message=message or f"Required dependency '{dependency}' is unavailable.",
            code="DEPENDENCY_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"dependency": dependency},
        )


class IngestionError(AppError):
    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to ingest '{filename}': {reason}",
            code="INGESTION_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"filename": filename, "reason": reason},
        )


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning(
        "Application error occurred",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=request_id,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
                **({"details": exc.details} if exc.details else {}),
            }
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning(
        "Request validation error",
        request_id=request_id,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters.",
                "request_id": request_id,
                "details": {"errors": exc.errors()},
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.exception(
        "Unhandled server error",
        request_id=request_id,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "request_id": request_id,
            }
        },
    )
