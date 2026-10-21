"""Dashboard & Analytics APIs for system usage, retrieval monitoring, and feedback metrics."""

from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])
