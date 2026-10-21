# Day 1 Log — Environment, Repository, Branching & Folder Structure

- **Date:** 2026-10-21
- **Day:** 1 of 21 (Week 1)
- **Status:** Complete & Aligned with Architectural Plan

---

## 1. Architectural Plan Alignment Review

The codebase was reviewed against the **"Enterprise RAG Platform – Vaibhav"** Workflow Diagram and System Architecture. The following alignments and adjustments were implemented:

1. **Vector Database (ChromaDB):**
   - Adopted **ChromaDB** as the primary vector store (as explicitly mandated in both the Workflow and System Architecture diagrams).
   - Configured `chromadb/chroma:0.5.5` in `docker-compose.yml` with persistent storage volume.
   - Built [`backend/app/retrieval/vectorstores/chroma.py`](../backend/app/retrieval/vectorstores/chroma.py) client wrapper.
   - Built ChromaDB-compatible `$and` / `$in` metadata payload filter generation in [`backend/app/retrieval/filters.py`](../backend/app/retrieval/filters.py).

2. **File Storage (AWS S3):**
   - Implemented [`backend/app/storage/s3.py`](../backend/app/storage/s3.py) to manage raw uploaded knowledge documents (PDF, Word, Excel, PowerPoint) in AWS S3 with transparent local disk fallback for offline development.

3. **Backend API Routes (FastAPI):**
   - Expanded API router in [`backend/app/api/v1/router.py`](../backend/app/api/v1/router.py) to match all backend layer domains:
     - Authentication & Authorization (`auth.py`)
     - User & Permission Management (`users.py`)
     - Document Processing APIs (`documents.py`)
     - RAG / Query APIs (`search.py`)
     - Chat History & Feedback APIs (`chat.py`, `feedback.py`)
     - Admin APIs (`admin.py`)
     - Dashboard & Analytics APIs (`analytics.py`)

4. **Orchestration & Cross-cutting Features:**
   - Added `langchain` and `langchain-community` dependencies for embedding and LLM generation.
   - Implemented conversational memory tracking in [`backend/app/generation/memory.py`](../backend/app/generation/memory.py) to support the "Memory (learn from interactions)" requirement.
   - Updated health readiness probe to check ChromaDB heartbeat alongside PostgreSQL and Redis.

---

## 2. What was accomplished today

1. **Repository & Governance Setup:**
   - Established `.gitignore`, `.gitattributes`, Apache-2.0 `LICENSE`, and standard PR template.
   - Configured Git branching workflow (`main`, `develop`, `feature/day-*`).

2. **Full Enterprise Scaffold:**
   - Generated the complete directory tree spanning all three weeks (`backend/app`, `data`, `infra`, `scripts`, `tests`, `docs`, `models_cache`).
   - Placed `.gitkeep` markers in empty directories so folder structures persist in version control.

3. **Dependency Management & Packaging:**
   - Configured `pyproject.toml` with pinned core runtime dependencies and modular optional sets (`ingestion`, `rag`, `eval`, `dev`).
   - Built `backend/Dockerfile` with multi-stage build awareness and `.dockerignore`.
   - Configured `docker-compose.yml` orchestrating FastAPI, ChromaDB, PostgreSQL 16, and Redis 7.

4. **FastAPI Application Core:**
   - Created `backend/app/main.py` with asynchronous request tracing middleware (`X-Request-ID` and latency logging).
   - Structured JSON logging setup via `structlog` with dedicated `audit` channel.
   - Custom `AppError` exception hierarchy with consistent JSON responses.
   - Liveness (`GET /api/v1/health`) and resilient readiness (`GET /api/v1/health/ready`) probes.

5. **Security by Design (RBAC):**
   - Implemented RBAC models (`employee`, `manager`, `admin`) and classification levels (`public`, `internal`, `confidential`, `restricted`).
   - Built vector store payload filter builders for ChromaDB and Qdrant.

6. **Quality Assurance & CI:**
   - Configured Ruff, Mypy, and pre-commit hooks (including blocks preventing raw data commits).
   - Authored pytest test suite with `tests/unit/test_health.py` and access-control security test suite `tests/security/test_access_control.py`.
   - Created GitHub Actions CI pipeline (`.github/workflows/ci.yml`).

7. **Documentation Baseline:**
   - Documented ADR-001 (`docs/adr/0001-tech-stack.md`) capturing technology choices and ChromaDB / S3 decisions.
   - Drafted system architecture and 6-stage workflow diagram in `docs/architecture/overview.md`.
   - Built `docs/datasets/DATA_SOURCES.md` and metadata templates.

---

## 3. Challenges & Notes

| Challenge | Impact | Resolution |
|---|---|---|
| **Docker command not found on Windows** | `docker compose up` fails if Docker Desktop is not installed or running. | Documented local Python execution path (`uvicorn app.main:app`) as an immediate alternative while Docker Desktop is installed. |
| **ChromaDB vs Qdrant Alignment** | Initial assumptions used Qdrant; architectural diagram mandates ChromaDB. | Updated stack to ChromaDB as primary vector DB, with Qdrant preserved as a secondary adapter. |
| **Raw Document Blob Storage** | Architecture requires AWS S3 for uploaded PDFs/Word/Excel/PPT. | Built `DocumentStorageManager` with transparent local filesystem fallback for offline development. |

---

## 4. Plan for Day 2

- Generate the synthetic enterprise corpus across PDF, DOCX, XLSX, and PPTX formats (`data/enterprise_demo/`).
- Build and execute the SEC EDGAR filing scraper (`scripts/download_sec_filings.py`) with compliant `User-Agent` headers and rate throttling.
- Download standard evaluation benchmarks (SQuAD, HotpotQA, BEIR SciFact, ARAGOG) into `data/evaluation/`.
