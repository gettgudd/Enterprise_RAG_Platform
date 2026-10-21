"""Security and Access Control Leakage Tests.

Ensures RBAC filters prevent unauthorized documents from being retrieved.
"""

import pytest
from app.retrieval.filters import build_access_filter, build_chroma_access_filter
from app.security.rbac import AccessLevel, Role, UserContext, has_access


def test_employee_cannot_retrieve_executive_strategy():
    """Placeholder test verifying that an employee cannot retrieve restricted executive strategy documents.

    Full integration with vector search is scheduled for Week 2.
    """
    pytest.skip("implemented Week 2")


def test_rbac_permission_matrix():
    """Unit test for RBAC permission levels."""
    emp = UserContext(user_id="1", username="emp", role=Role.EMPLOYEE, department="Engineering")
    mgr = UserContext(user_id="2", username="mgr", role=Role.MANAGER, department="Engineering")
    adm = UserContext(user_id="3", username="adm", role=Role.ADMIN, department="IT")

    # Employee
    assert has_access(emp, AccessLevel.PUBLIC) is True
    assert has_access(emp, AccessLevel.INTERNAL) is True
    assert has_access(emp, AccessLevel.CONFIDENTIAL) is False
    assert has_access(emp, AccessLevel.RESTRICTED) is False

    # Manager
    assert has_access(mgr, AccessLevel.PUBLIC) is True
    assert has_access(mgr, AccessLevel.INTERNAL) is True
    assert has_access(mgr, AccessLevel.CONFIDENTIAL) is True
    assert has_access(mgr, AccessLevel.RESTRICTED) is False

    # Admin
    assert has_access(adm, AccessLevel.PUBLIC) is True
    assert has_access(adm, AccessLevel.INTERNAL) is True
    assert has_access(adm, AccessLevel.CONFIDENTIAL) is True
    assert has_access(adm, AccessLevel.RESTRICTED) is True


def test_build_access_filter():
    """Unit test for generic/Qdrant payload filter generation."""
    emp_filter = build_access_filter("employee", "Engineering")
    assert emp_filter["must"][0]["match"]["any"] == ["public", "internal"]
    assert "Engineering" in emp_filter["must"][1]["match"]["any"]

    admin_filter = build_access_filter("admin")
    assert "restricted" in admin_filter["must"][0]["match"]["any"]
    assert len(admin_filter["must"]) == 1  # Admin has no department restriction


def test_build_chroma_access_filter():
    """Unit test for ChromaDB metadata where filter generation."""
    chroma_filter = build_chroma_access_filter("employee", "Engineering")
    assert "$and" in chroma_filter
    levels = chroma_filter["$and"][0]["access_level"]["$in"]
    assert "public" in levels and "internal" in levels and "confidential" not in levels

    admin_chroma_filter = build_chroma_access_filter("admin")
    assert "access_level" in admin_chroma_filter
    assert "restricted" in admin_chroma_filter["access_level"]["$in"]
