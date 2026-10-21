"""Document ingestion and management endpoints (Day 4+)."""

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])
