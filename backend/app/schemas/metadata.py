"""Metadata schemas for document registration, RBAC classification, and catalog governance."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class AccessLevel(str, Enum):
    """Role-Based Access Control (RBAC) data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Department(str, Enum):
    """Business organizational departments."""
    HR = "Human Resources"
    ENGINEERING = "Engineering"
    FINANCE = "Finance"
    LEGAL = "Legal"
    EXECUTIVE = "Executive"
    COMPANY_WIDE = "company-wide"


class DocumentType(str, Enum):
    """Supported document formats."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    HTML = "html"
    TXT = "txt"


class DocumentMetadata(BaseModel):
    """Standardized metadata record for a document in the knowledge corpus."""
    document_id: str = Field(..., description="Unique alphanumeric identifier (e.g. DOC-ENG-001)")
    filename: str = Field(..., description="Original filename with extension")
    department: str = Field(..., description="Business department owner")
    owner: str = Field(..., description="Email address or username of document owner")
    access_level: AccessLevel = Field(..., description="Security classification tier")
    document_type: DocumentType = Field(..., description="Document file format")
    version: str = Field(default="1.0", description="Semantic document version")
    created_at: datetime = Field(..., description="ISO 8601 creation timestamp")
    source: Literal["synthetic", "sec_edgar", "external", "benchmark"] = Field(
        ..., description="Provenance source category"
    )
    description: Optional[str] = Field(default=None, description="Executive summary of contents")
    checksum_sha256: Optional[str] = Field(default=None, description="SHA256 hex digest for integrity")
    page_count: Optional[int] = Field(default=None, description="Number of pages or slides")
    file_size_bytes: Optional[int] = Field(default=None, description="File size on disk in bytes")


class RolePermission(BaseModel):
    """Permissions granted to a security role."""
    description: str
    allowed_access_levels: List[AccessLevel]
    allowed_departments: List[str]


class UserRecord(BaseModel):
    """Sample user record for security and RBAC testing."""
    user_id: str
    username: str
    role: str
    department: str


class AccessMatrix(BaseModel):
    """Full role-based access control matrix definition."""
    roles: Dict[str, RolePermission]
    sample_users: List[UserRecord]
