"""Unit tests for Day 2 dataset preparation, schemas, and scraping logic."""

import json
import time
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.schemas.metadata import (
    AccessLevel,
    AccessMatrix,
    Department,
    DocumentMetadata,
    DocumentType,
)
from scripts.download_sec_filings import RateLimiter
from scripts.generate_synthetic_docs import CORPUS_SPEC
from scripts.validate_datasets import check_magic_bytes


class TestMetadataSchemas:
    """Test suite for Document Metadata and Access Matrix Pydantic validation."""

    def test_valid_document_metadata(self) -> None:
        valid_payload = {
            "document_id": "DOC-HR-001",
            "filename": "employee_handbook.pdf",
            "department": "Human Resources",
            "owner": "hr@enterprise.internal",
            "access_level": "internal",
            "document_type": "pdf",
            "version": "1.0",
            "created_at": "2026-01-15T09:00:00Z",
            "source": "synthetic",
            "description": "Standard company handbook",
            "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        doc = DocumentMetadata(**valid_payload)
        assert doc.document_id == "DOC-HR-001"
        assert doc.access_level == AccessLevel.INTERNAL
        assert doc.document_type == DocumentType.PDF

    def test_invalid_access_level_raises_validation_error(self) -> None:
        invalid_payload = {
            "document_id": "DOC-HR-002",
            "filename": "benefits.docx",
            "department": "Human Resources",
            "owner": "hr@enterprise.internal",
            "access_level": "top_secret",  # Invalid classification tier
            "document_type": "docx",
            "created_at": "2026-01-15T09:00:00Z",
            "source": "synthetic",
        }
        with pytest.raises(ValidationError):
            DocumentMetadata(**invalid_payload)

    def test_access_matrix_validation(self) -> None:
        matrix_payload = {
            "roles": {
                "admin": {
                    "description": "Super admin with unrestricted access",
                    "allowed_access_levels": ["public", "internal", "confidential", "restricted"],
                    "allowed_departments": ["*"],
                },
                "employee": {
                    "description": "Standard contributor",
                    "allowed_access_levels": ["public", "internal"],
                    "allowed_departments": ["own_department", "company-wide"],
                },
            },
            "sample_users": [
                {
                    "user_id": "usr-01",
                    "username": "alice",
                    "role": "admin",
                    "department": "IT",
                }
            ],
        }
        matrix = AccessMatrix(**matrix_payload)
        assert "admin" in matrix.roles
        assert AccessLevel.RESTRICTED in matrix.roles["admin"].allowed_access_levels
        assert len(matrix.sample_users) == 1


class TestDatasetIntegrityAndScraper:
    """Test suite for corpus specification, SEC rate limiting, and binary headers."""

    def test_corpus_spec_uniqueness_and_needles(self) -> None:
        """Ensure all corpus documents have unique IDs and embedded needle facts."""
        seen_ids = set()
        for doc in CORPUS_SPEC:
            doc_id = doc["document_id"]
            assert doc_id not in seen_ids, f"Duplicate document_id found: {doc_id}"
            seen_ids.add(doc_id)
            assert doc["needle_fact"], f"Missing ground-truth needle fact in {doc_id}"
            assert doc["access_level"] in {"public", "internal", "confidential", "restricted"}
            assert doc["document_type"] in {"pdf", "docx", "xlsx", "pptx"}

    def test_sec_edgar_rate_limiter(self) -> None:
        """Verify rate limiter enforces minimum interval between calls."""
        rate = 10.0  # 10 calls / sec = 0.1s interval
        limiter = RateLimiter(max_per_second=rate)
        
        t0 = time.time()
        limiter.wait()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - t0
        # 3 calls with 0.1s interval should take at least ~0.20s total
        assert elapsed >= 0.18

    def test_magic_bytes_detection(self, tmp_path: Path) -> None:
        """Verify magic byte verification on synthetic headers."""
        # PDF test
        pdf_file = tmp_path / "sample.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n1 0 obj\n")
        ok, msg = check_magic_bytes(pdf_file, "pdf")
        assert ok is True

        # DOCX / Zip test
        docx_file = tmp_path / "sample.docx"
        docx_file.write_bytes(b"\x50\x4B\x03\x04\x14\x00\x06\x00")
        ok, msg = check_magic_bytes(docx_file, "docx")
        assert ok is True

        # Corrupted header test
        corrupt_file = tmp_path / "corrupt.pdf"
        corrupt_file.write_bytes(b"INVALID_HEADER_DATA")
        ok, msg = check_magic_bytes(corrupt_file, "pdf")
        assert ok is False
