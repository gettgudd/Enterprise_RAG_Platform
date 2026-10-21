from typing import Literal
from pydantic import BaseModel, Field


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    app: str = "enterprise-rag-platform"
    version: str = "0.1.0"


class ReadinessDependencies(BaseModel):
    postgres: str = Field(description="PostgreSQL database status ('up' or 'down')")
    vector_db: str = Field(description="Vector store (ChromaDB / Qdrant) status ('up' or 'down')")
    redis: str = Field(description="Redis cache status ('up' or 'down')")


class ReadinessResponse(BaseModel):
    status: Literal["ok", "degraded", "down"]
    app: str = "enterprise-rag-platform"
    version: str = "0.1.0"
    dependencies: ReadinessDependencies
