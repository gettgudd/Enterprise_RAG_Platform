# Enterprise RAG Platform

[![CI Pipeline](https://github.com/your-org/enterprise-rag-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/enterprise-rag-platform/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-v0.5.5-orange.svg)](https://www.trychroma.com/)

A production-grade, enterprise-ready **Retrieval-Augmented Generation (RAG) Platform** built with **FastAPI**, **ChromaDB**, **PostgreSQL**, **AWS S3**, and **React**.

Designed to ingest diverse unstructured corporate knowledge files (**PDF, Word, Excel, PowerPoint**), enforce **Role-Based Access Control (RBAC)** at the retrieval layer, provide grounded citations, track multi-turn conversational memory, capture user feedback, and power continuous learning.

---

## 🏛️ System Architecture

*Directly aligned with the "Enterprise RAG Platform – Vaibhav" architectural plan:*

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. USERS                                                                               │
│ Employees (Eng, HR, Finance) ──► Managers (Access Control) ──► Admins (Permissions)   │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND (React)                                                                    │
│ Document Upload │ Chat Interface │ Chat History │ Feedback (👍/👎) │ User Admin │ Analytics│
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │ HTTPS API Calls
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. BACKEND (FastAPI REST API)                                                          │
│ - Auth (JWT/OAuth)            - Document Processing APIs    - RAG / Query APIs         │
│ - Chat & Feedback APIs        - User & Permission Mgmt      - Admin & Analytics APIs   │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. RAG PIPELINE (LangChain / LlamaIndex)                                               │
│ Document Ingestion ──► Embedding Generation ──► Vector Storage ──► Hybrid Retrieval   │
│                        (BAAI/bge-small-en)      (ChromaDB)          & LLM Generation   │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. DATA & STORAGE LAYER                                                                │
│ - ChromaDB (Vector DB): Document embeddings, text chunks, and metadata                 │
│ - PostgreSQL 16 (App DB): Users, permissions, chat history, feedback                   │
│ - AWS S3: Durable raw document storage (PDF, Word, Excel, PPT)                         │
│ - Redis 7: Cache, session state, and background task queue                             │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. DEPLOYMENT (AWS Cloud)                                                              │
│ AWS EC2/ECS │ AWS S3 │ AWS RDS (PostgreSQL) │ AWS ECR/EKS (Docker) │ AWS CloudFront   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

For full details, see [Architecture & Workflow Blueprint](docs/architecture/overview.md) and [ADR-001: Technology Stack](docs/adr/0001-tech-stack.md).

---

## 6-Stage End-to-End Workflow

1. **Document Upload:** Single or bulk upload of enterprise knowledge files (**PDF, Word, Excel, PPT**).
2. **Document Processing:** Parse file formats, clean/chunk text, generate embeddings via LangChain/LlamaIndex, store in **ChromaDB**.
3. **Query & Retrieval:** Natural language question, semantic search with RBAC payload filters, retrieve top-K relevant chunks with source citations.
4. **LLM Augmentation:** Context + query prompt assembly, LLM generation with page-level citations.
5. **Response to User:** AI answer with citations, source references, chat history persistence, feedback collection (thumbs up/down), memory update.
6. **Continuous Learning:** Feedback analysis, knowledge base updates, fine-tuning, and usage monitoring.

---

## ⚡ Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Option A: Run via Docker Compose (Multi-container stack)
```bash
docker compose up -d --build
```
> **Note:** Requires Docker Desktop to be installed and running.

Services started:
* **FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
* **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ChromaDB Vector Store:** [http://localhost:8001](http://localhost:8001)
* **PostgreSQL 16:** `localhost:5432`
* **Redis 7:** `localhost:6379`

### 3. Option B: Run Locally (Without Docker)
If Docker is not currently installed on your workstation, you can run the backend directly:
```bash
# 1. Create Python virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e ".[dev,rag]"

# 3. Start the FastAPI development server
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 4. Health & Readiness Verification
```bash
# Liveness probe
curl http://localhost:8000/api/v1/health

# Readiness probe (probes Postgres, ChromaDB, and Redis)
curl http://localhost:8000/api/v1/health/ready
```

---

## 🧪 Testing

```bash
# Run unit and security tests
pytest

# Code quality checks
ruff check .
mypy backend/app
```
