"""Authentication & Authorization endpoints (JWT / OAuth) per architecture plan."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
