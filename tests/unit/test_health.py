from unittest.mock import patch
from fastapi.testclient import TestClient


def test_liveness(client: TestClient) -> None:
    """Test the liveness check returns 200 without checking external dependencies."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data
    assert "X-Request-ID" in response.headers


@patch("app.api.v1.health.ping_database", return_value=True)
@patch("redis.Redis.from_url")
@patch("httpx.AsyncClient.get")
def test_readiness_healthy(mock_http_get, mock_redis_from_url, mock_ping_db, client: TestClient) -> None:
    """Test readiness check when all services respond positively."""
    mock_redis_client = mock_redis_from_url.return_value
    mock_redis_client.ping.return_value = True

    mock_http_response = mock_http_get.return_value
    mock_http_response.status_code = 200

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["dependencies"]["postgres"] == "up"
    assert data["dependencies"]["vector_db"] == "up"
    assert data["dependencies"]["redis"] == "up"


@patch("app.api.v1.health.ping_database", return_value=False)
def test_readiness_unhealthy_when_db_down(mock_ping_db, client: TestClient) -> None:
    """Test readiness check returns 503 when PostgreSQL is down."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "down"
    assert data["dependencies"]["postgres"] == "down"
