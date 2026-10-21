"""Admin APIs for system configuration, vector index management, and continuous learning."""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])
