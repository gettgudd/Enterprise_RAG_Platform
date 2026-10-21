from typing import Any
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    request_id: str = Field(..., description="Unique request tracing ID")
    details: dict[str, Any] | None = Field(default=None, description="Optional supplemental details")


class ErrorResponse(BaseModel):
    error: ErrorDetail
