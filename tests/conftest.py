import os
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient

# Ensure test environment variables before importing app
os.environ["APP_ENV"] = "test"
os.environ["POSTGRES_USER"] = "rag_test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "rag_test"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["QDRANT_HOST"] = "localhost"
os.environ["QDRANT_PORT"] = "6333"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture with app lifecycle."""
    with TestClient(app) as test_client:
        yield test_client
