"""FastAPI dependency injection utilities."""

from collections.abc import Generator
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db


def get_app_settings() -> Settings:
    """Inject application settings."""
    return get_settings()


def get_database_session(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    """Inject database session."""
    yield db


def get_request_id(request: Request) -> str:
    """Retrieve unique request ID assigned by tracing middleware."""
    return getattr(request.state, "request_id", "unknown")
