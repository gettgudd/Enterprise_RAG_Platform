"""Access-control filter builder for ChromaDB and Qdrant vector stores.

Enforces role-based security filters at the retrieval level to prevent
unauthorized documents from ever entering the context window.
"""

from typing import Any


def build_chroma_access_filter(user_role: str, department: str | None = None) -> dict[str, Any] | None:
    """Construct a ChromaDB metadata 'where' filter matching documents accessible to the specified role.

    Roles:
      - admin: can access all documents (public, internal, confidential, restricted)
      - manager: can access public, internal, and confidential documents
      - employee: can access public and internal documents
    """
    role_hierarchy: dict[str, list[str]] = {
        "admin": ["public", "internal", "confidential", "restricted"],
        "manager": ["public", "internal", "confidential"],
        "employee": ["public", "internal"],
    }

    allowed_levels = role_hierarchy.get(user_role.lower(), ["public"])

    conditions: list[dict[str, Any]] = [
        {"access_level": {"$in": allowed_levels}}
    ]

    if department and user_role.lower() != "admin":
        conditions.append({
            "department": {"$in": [department, "all", "company-wide"]}
        })

    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def build_access_filter(user_role: str, department: str | None = None) -> dict[str, Any]:
    """Default Qdrant/generic payload filter builder."""
    role_hierarchy: dict[str, list[str]] = {
        "admin": ["public", "internal", "confidential", "restricted"],
        "manager": ["public", "internal", "confidential"],
        "employee": ["public", "internal"],
    }

    allowed_levels = role_hierarchy.get(user_role.lower(), ["public"])

    filters: dict[str, Any] = {
        "must": [
            {
                "key": "access_level",
                "match": {"any": allowed_levels},
            }
        ]
    }

    if department and user_role.lower() != "admin":
        filters["must"].append({
            "key": "department",
            "match": {"any": [department, "all", "company-wide"]},
        })

    return filters
