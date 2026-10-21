"""RAG benchmark evaluation and metrics endpoints (Week 3)."""

from fastapi import APIRouter

router = APIRouter(prefix="/evaluation", tags=["evaluation"])
