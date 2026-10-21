import httpx
from fastapi import APIRouter, Response, status
import redis

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import ping_database
from app.schemas.health import LivenessResponse, ReadinessDependencies, ReadinessResponse

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get(
    "/health",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Returns 200 if the FastAPI application process is alive without checking downstream dependencies.",
)
async def liveness_check() -> LivenessResponse:
    return LivenessResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={
        200: {"description": "All dependencies are healthy and reachable."},
        503: {"description": "One or more downstream dependencies are unavailable."},
    },
    summary="Readiness check",
    description="Probes PostgreSQL, Vector Store (ChromaDB/Qdrant), and Redis with strict timeouts.",
)
async def readiness_check(response: Response) -> ReadinessResponse:
    # 1. Probe PostgreSQL
    postgres_up = ping_database(timeout_seconds=2.0)
    postgres_status = "up" if postgres_up else "down"

    # 2. Probe Vector Store (ChromaDB or Qdrant)
    vector_status = "down"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            if settings.vector_db_type == "chromadb":
                chroma_url = f"http://{settings.chroma_host}:{settings.chroma_port}/api/v1/heartbeat"
                res = await client.get(chroma_url)
                if res.status_code == 200:
                    vector_status = "up"
            else:
                qdrant_url = f"http://{settings.qdrant_host}:{settings.qdrant_port}/readyz"
                res = await client.get(qdrant_url)
                if res.status_code == 200:
                    vector_status = "up"
    except Exception as exc:
        logger.debug("Vector store health probe error", error=str(exc))
        vector_status = "down"

    # 3. Probe Redis
    redis_status = "down"
    try:
        r = redis.Redis.from_url(settings.redis_url, socket_timeout=2.0)
        if r.ping():
            redis_status = "up"
        r.close()
    except Exception as exc:
        logger.debug("Redis health probe error", error=str(exc))
        redis_status = "down"

    is_all_up = (
        postgres_status == "up" and vector_status == "up" and redis_status == "up"
    )

    if not is_all_up:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ok" if is_all_up else "down",
        app=settings.app_name,
        version=settings.app_version,
        dependencies=ReadinessDependencies(
            postgres=postgres_status,
            vector_db=vector_status,
            redis=redis_status,
        ),
    )
