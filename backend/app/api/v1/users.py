"""User & Permission Management endpoints (Employees, Managers, Admins) per architecture plan."""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])
