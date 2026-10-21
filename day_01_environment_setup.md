# Day 1 — Environment, Repository, Branching & Folder Structure

**Project:** Enterprise RAG Platform
**Week 1 / Day 1 of 21**
**Estimated effort:** 6–8 hours
**Goal of the day:** At the end of today, anyone can clone the repo, run one command, and get a running (empty) backend, database, vector store, and test suite — with the full folder structure and data layout in place.

---

## 0. Assumptions (change these now if they are wrong)

Your uploaded plan covers datasets only, so these choices are mine. Changing them later is expensive, so confirm them today.

| Area | Assumed choice | Reason |
|---|---|---|
| Language | Python 3.11 | Best RAG/ML ecosystem |
| API framework | FastAPI | Async, auto OpenAPI docs, strong portfolio signal |
| Metadata DB | PostgreSQL 16 | Documents, chunks metadata, users, feedback |
| Vector store | Qdrant (Docker) | Payload filtering is needed for access control |
| Keyword search | BM25 (`rank_bm25` first, OpenSearch optional later) | Needed for hybrid retrieval (BEIR/SciFact use) |
| Cache/queue (optional) | Redis | Ingestion jobs later |
| Frontend | React + Vite (Week 2) | Placeholder folder only today |
| Packaging | Docker + Docker Compose | One-command setup |
| Dependency mgmt | `uv` (or `pip` + `venv`) | Fast, reproducible |
| Lint/format | Ruff + Black-compatible formatting, mypy | Quality gate |
| Tests | pytest | Standard |
| CI | GitHub Actions | Free, visible on portfolio |

---

## 1. Day 1 Task Overview

| # | Task | Output | Est. |
|---|---|---|---|
| 1 | Install & verify local prerequisites | Tools verified | 30 min |
| 2 | Create GitHub repo and local clone | Repo exists | 15 min |
| 3 | Define branching strategy and protect branches | Branches + rules | 30 min |
| 4 | Create full folder structure (code, data, docs, infra) | Tree committed | 60 min |
| 5 | Python environment and dependency files | `pyproject.toml`, lock file | 45 min |
| 6 | Configuration and secrets management | `.env.example`, settings module | 45 min |
| 7 | Docker Compose (API, Postgres, Qdrant, Redis) | `docker-compose.yml` | 60 min |
| 8 | Minimal FastAPI app with health check | `/health` works | 45 min |
| 9 | Logging, error handling skeleton | `core/logging.py` | 30 min |
| 10 | Code quality tooling (ruff, mypy, pre-commit) | Hooks active | 30 min |
| 11 | Test setup and first tests | Passing pytest | 30 min |
| 12 | Makefile developer commands | `make up`, `make test` | 20 min |
| 13 | CI pipeline | Green GitHub Action | 30 min |
| 14 | Data directory skeleton and dataset licence tracking | `data/` tree + `DATA_SOURCES.md` | 30 min |
| 15 | Documentation baseline (README, ADRs) | README + ADR-001 | 30 min |
| 16 | Commit, push, merge to `develop`, verify | Day 1 tag | 20 min |

---

## 2. Task 1 — Local Prerequisites

### Features / actions
Install and verify:

```bash
git --version            # >= 2.40
python3 --version        # 3.11.x
docker --version         # >= 24
docker compose version   # v2
make --version
uv --version             # or: pip install uv
node --version           # >= 20 (needed for Week 2 frontend, install now)
```

Recommended extras: VS Code (or PyCharm), the Docker, Python, Ruff and GitLens extensions, and a REST client (Bruno, Postman or the `httpie` CLI).

Hardware checks:
- At least 16 GB RAM is recommended (embedding models + Qdrant + Postgres).
- At least 20 GB free disk (datasets plus model downloads).
- GPU is optional. Plan CPU-friendly embedding models.

### Challenges
- Docker Desktop needs WSL2 on Windows. Make sure the repo lives **inside the WSL filesystem**, not `/mnt/c`, or file I/O will be very slow.
- Apple Silicon: some images need `platform: linux/amd64`. Check this for Qdrant/Postgres images.
- Corporate proxies can block `pip`/Docker pulls.

### Done when
All version commands above return successfully.

---

## 3. Task 2 — Repository Creation

```bash
mkdir enterprise-rag-platform && cd enterprise-rag-platform
git init -b main
gh repo create enterprise-rag-platform --private --source=. --remote=origin
# make public later, only after dataset licences are checked
```

Create initially:
- `README.md` (stub)
- `.gitignore` (see Task 5)
- `LICENSE` (MIT or Apache-2.0)
- `.gitattributes` (normalise line endings and mark data as binary)

```gitattributes
* text=auto eol=lf
*.pdf  binary
*.docx binary
*.xlsx binary
*.pptx binary
```

### Challenges
- Keep the repo **private** until the data licence review (your plan, section 20: check licence before redistributing).
- Never commit large datasets. Decide today that `data/` content is git-ignored except placeholders and metadata.

---

## 4. Task 3 — Branching Strategy

### Model: simplified Git Flow

```text
main        ← stable, tagged releases only (v0.1.0, v0.2.0, v1.0.0)
  │
develop     ← integration branch; all features merge here
  │
  ├── feature/day-01-project-setup
  ├── feature/day-02-dataset-preparation
  ├── feature/day-03-document-parsing
  ├── feature/day-04-chunking-ingestion
  ├── feature/day-05-embeddings-vectorstore
  ├── feature/day-06-hybrid-retrieval
  └── feature/day-07-retrieval-evaluation
```

Additional prefixes: `fix/…`, `docs/…`, `chore/…`, `hotfix/…` (from `main`).

### Commands

```bash
git add . && git commit -m "chore: initial commit"
git push -u origin main
git checkout -b develop && git push -u origin develop
git checkout -b feature/day-01-project-setup develop
```

### Conventions
- **Commit messages:** Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`, `ci:`.
- **Pull requests:** Every feature → PR into `develop`, even working solo (it builds a visible history).
- **Merge method:** Squash-merge into `develop`; merge commit from `develop` → `main`.
- **Tags:** `v0.1.0` at the end of Week 1.

### Branch protection (GitHub → Settings → Branches)
- `main`: require PR, require CI to pass, no direct pushes.
- `develop`: require CI to pass.

Add `.github/pull_request_template.md`:

```markdown
## What
## Why
## How tested
## Checklist
- [ ] Tests added/updated
- [ ] Docs updated
- [ ] No secrets or data files committed
- [ ] Access-control impact considered
```

### Challenges
- Branch protection on private repos may need a paid plan. If unavailable, enforce via discipline and the pre-commit hook.
- Resist working directly on `develop`.

---

## 5. Task 4 — Full Folder Structure (the part that was missing)

Create **all** of the following today, even if folders are empty (use `.gitkeep`). Week 2–3 code then has a defined home.

```text
enterprise-rag-platform/
│
├── README.md
├── LICENSE
├── Makefile
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml
├── .dockerignore
├── docker-compose.yml
├── docker-compose.override.yml          # local dev overrides (hot reload)
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   └── pull_request_template.md
│
├── backend/
│   ├── Dockerfile
│   └── app/
│       ├── __init__.py
│       ├── main.py                      # FastAPI entrypoint
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py                # pydantic-settings
│       │   ├── logging.py               # structured logging
│       │   ├── exceptions.py            # custom exceptions + handlers
│       │   └── security.py              # (Week 2) auth, JWT, roles
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py                  # dependency injection
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py
│       │       ├── health.py
│       │       ├── documents.py         # (Day 4+)
│       │       ├── search.py            # (Day 6)
│       │       ├── chat.py              # (Week 2)
│       │       ├── feedback.py          # (Week 3)
│       │       └── evaluation.py        # (Week 3)
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   ├── session.py
│       │   ├── base.py
│       │   ├── models/                  # SQLAlchemy models
│       │   │   └── __init__.py
│       │   └── migrations/              # Alembic
│       │
│       ├── schemas/                     # Pydantic request/response models
│       │   └── __init__.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── parsers/                 # pdf, docx, xlsx, pptx, email
│       │   │   └── __init__.py
│       │   ├── cleaning/
│       │   ├── chunking/
│       │   ├── metadata/
│       │   └── pipeline.py
│       │
│       ├── embeddings/
│       │   ├── __init__.py
│       │   └── providers/               # local (sentence-transformers), API-based
│       │
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── dense.py
│       │   ├── bm25.py
│       │   ├── hybrid.py
│       │   ├── reranker.py
│       │   ├── filters.py               # access-control filter builder
│       │   └── vectorstores/            # qdrant client wrapper
│       │
│       ├── generation/                  # (Week 2)
│       │   ├── __init__.py
│       │   ├── prompts/
│       │   ├── llm_clients/
│       │   └── citations.py
│       │
│       ├── security/                    # (Week 2) permission-aware retrieval
│       │   ├── __init__.py
│       │   ├── rbac.py
│       │   └── guardrails.py
│       │
│       ├── evaluation/                  # (Week 3)
│       │   ├── __init__.py
│       │   ├── metrics/
│       │   ├── datasets/                # converters → common eval format
│       │   └── runners/
│       │
│       ├── feedback/                    # (Week 3)
│       │   └── __init__.py
│       │
│       └── utils/
│           └── __init__.py
│
├── frontend/                            # (Week 2) React + Vite
│   └── .gitkeep
│
├── scripts/
│   ├── bootstrap.sh                     # one-time setup helper
│   ├── generate_synthetic_docs.py       # Day 2
│   ├── download_sec_filings.py          # Day 2
│   ├── download_eval_datasets.py        # Day 2
│   ├── ingest_corpus.py                 # Day 4
│   └── run_eval.py                      # Day 7
│
├── data/                                # git-ignored content (see .gitignore)
│   ├── README.md
│   ├── enterprise_demo/
│   │   ├── pdf/
│   │   ├── docx/
│   │   ├── xlsx/
│   │   └── pptx/
│   ├── sec_edgar/
│   │   ├── company_01/
│   │   ├── company_02/
│   │   └── company_03/
│   ├── evaluation/
│   │   ├── squad/
│   │   ├── hotpotqa/
│   │   ├── scifact/
│   │   ├── natural_questions/
│   │   └── aragog/
│   ├── enron/                           # optional dataset
│   ├── metadata/                        # document metadata JSON, ACL matrix
│   ├── processed/                       # parsed text, chunks (generated)
│   └── eval_internal/                   # converted common-format eval sets
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_health.py
│   ├── integration/
│   ├── security/                        # access-control leakage tests
│   └── fixtures/
│       └── sample_docs/
│
├── docs/
│   ├── architecture/
│   │   └── overview.md
│   ├── adr/
│   │   └── 0001-tech-stack.md
│   ├── datasets/
│   │   └── DATA_SOURCES.md
│   ├── api/
│   ├── runbooks/
│   └── daily_log/
│       └── day_01.md
│
├── notebooks/                           # exploration only; no business logic
│   └── .gitkeep
│
├── infra/
│   ├── docker/
│   ├── postgres/
│   │   └── init.sql
│   └── qdrant/
│
└── models_cache/                        # git-ignored HF / embedding model cache
    └── .gitkeep
```

### Create it quickly

```bash
# top-level
mkdir -p .github/workflows backend/app frontend scripts tests docs notebooks infra models_cache

# backend packages
for d in core api/v1 db/models db/migrations schemas \
         ingestion/parsers ingestion/cleaning ingestion/chunking ingestion/metadata \
         embeddings/providers retrieval/vectorstores \
         generation/prompts generation/llm_clients \
         security evaluation/metrics evaluation/datasets evaluation/runners \
         feedback utils; do
  mkdir -p backend/app/$d
  touch backend/app/$d/__init__.py
done
touch backend/app/__init__.py backend/app/main.py

# data layout (matches section 12 of the dataset plan, plus extras)
mkdir -p data/enterprise_demo/{pdf,docx,xlsx,pptx} \
         data/sec_edgar/company_{01,02,03} \
         data/evaluation/{squad,hotpotqa,scifact,natural_questions,aragog} \
         data/enron data/metadata data/processed data/eval_internal

# tests & docs
mkdir -p tests/{unit,integration,security,fixtures/sample_docs} \
         docs/{architecture,adr,datasets,api,runbooks,daily_log} \
         infra/{docker,postgres,qdrant}

# keep empty dirs in git
find . -type d -empty -not -path "./.git/*" -exec touch {}/.gitkeep \;
```

### Why this structure (design rules to follow all 3 weeks)
1. **Separation of layers:** API → services → retrieval/ingestion → stores. Routes contain no business logic.
2. **Swappable providers:** embeddings, vector stores and LLM clients sit behind interfaces so you can swap them.
3. **Security is a first-class folder:** `retrieval/filters.py`, `security/` and `tests/security/` exist from Day 1.
4. **Data is separate from code:** `data/` is never imported by the app. Scripts reference it via config.
5. **Evaluation is separate from the app:** it can run offline as scripts and as an API.

### Challenges
- **Over-engineering:** do not fill the empty modules today. Stubs only.
- **Circular imports** between `retrieval`, `security` and `db`. Keep dependencies one-directional: `api → services → (retrieval, ingestion, generation) → (db, vectorstores)`.
- **Empty folders vanish in Git.** Use `.gitkeep`.
- **Naming drift** from your dataset plan: `data/` must match section 12 exactly (`enterprise_demo`, `sec_edgar`, `evaluation`, `enron`).

---

## 6. Task 5 — Python Environment & Dependencies

### `.gitignore` (essentials)

```gitignore
# Python
__pycache__/
*.pyc
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/

# Secrets
.env
*.pem
*.key

# Data (large / licence-restricted)
data/enterprise_demo/**/*
data/sec_edgar/**/*
data/evaluation/**/*
data/enron/**/*
data/processed/**/*
data/eval_internal/**/*
!data/**/.gitkeep
!data/README.md
!data/metadata/

# Models & caches
models_cache/*
!models_cache/.gitkeep

# Docker / OS / IDE
.DS_Store
.idea/
.vscode/*
!.vscode/settings.json
node_modules/
```

> **Decision:** the synthetic documents are *yours*, so you may later commit a small sample under `tests/fixtures/sample_docs/` and publish the generator script, rather than the full corpus.

### `pyproject.toml` (starter)

```toml
[project]
name = "enterprise-rag-platform"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "pydantic>=2",
  "pydantic-settings",
  "sqlalchemy>=2",
  "alembic",
  "psycopg[binary]",
  "qdrant-client",
  "httpx",
  "structlog",
  "python-multipart",
]

[project.optional-dependencies]
ingestion = ["pypdf", "pdfplumber", "python-docx", "openpyxl", "python-pptx", "unstructured"]
ml        = ["sentence-transformers", "rank-bm25", "numpy"]
eval      = ["datasets", "beir", "ranx", "pandas"]
dev       = ["pytest", "pytest-asyncio", "pytest-cov", "ruff", "mypy", "pre-commit"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "S"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
```

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Install the heavy groups (`ml`, `ingestion`, `eval`) only when needed on Days 3–7.

### Challenges
- `unstructured` and `torch` are large and slow to install. Defer them.
- Pin versions after everything works (`uv lock`) so the setup is reproducible.
- Python 3.12+ can break some ML wheels. Stay on 3.11.

---

## 7. Task 6 — Configuration & Secrets

### `.env.example` (committed). Copy to `.env` (git-ignored).

```env
# App
APP_ENV=local
APP_NAME=enterprise-rag-platform
LOG_LEVEL=INFO
API_PORT=8000

# Postgres
POSTGRES_USER=rag
POSTGRES_PASSWORD=change_me
POSTGRES_DB=rag
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=enterprise_chunks

# Redis
REDIS_URL=redis://redis:6379/0

# Embeddings
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384

# LLM (Week 2)
LLM_PROVIDER=
LLM_API_KEY=

# Auth (Week 2)
JWT_SECRET=change_me
JWT_EXPIRE_MINUTES=60

# Paths
DATA_DIR=/app/data
MODEL_CACHE_DIR=/app/models_cache
```

### `backend/app/core/config.py` (shape)

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_name: str = "enterprise-rag-platform"
    log_level: str = "INFO"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "enterprise_chunks"

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    data_dir: str = "data"

    @property
    def database_url(self) -> str:
        return (f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Challenges
- Hostnames differ: `postgres` inside Docker vs `localhost` from your host. Keep two clear settings paths.
- **Embedding dimension must match the Qdrant collection.** Changing the model later means re-indexing everything. Record this in the ADR.
- Never log secrets.

---

## 8. Task 7 — Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    env_file: .env
    ports: ["8000:8000"]
    volumes:
      - ./backend/app:/app/app
      - ./data:/app/data
      - ./models_cache:/app/models_cache
    depends_on:
      postgres: { condition: service_healthy }
      qdrant:   { condition: service_started }
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      retries: 10

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes: [qdrantdata:/qdrant/storage]

  redis:
    image: redis:7
    ports: ["6379:6379"]

volumes:
  pgdata:
  qdrantdata:
```

`backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> Adjust the build context (`context: .`, `dockerfile: backend/Dockerfile`) since `pyproject.toml` lives in the repo root.

### Challenges
- Port conflicts (5432, 6379, 8000). Change the host-side port if they are in use.
- Pin the Qdrant image tag instead of `latest` once it works.
- Volumes must persist between restarts, or you will re-index on every run.
- Mounting `./data` into the container is convenient but slow on Windows/macOS file shares.

---

## 9. Task 8 — Minimal FastAPI App + Health Check

`backend/app/main.py`:

```python
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="Enterprise RAG Platform", version="0.1.0")
app.include_router(api_router, prefix="/api/v1")
```

`api/v1/health.py` should return:

```json
{
  "status": "ok",
  "app": "enterprise-rag-platform",
  "version": "0.1.0",
  "dependencies": { "postgres": "up", "qdrant": "up", "redis": "up" }
}
```

Features to implement:
- `GET /api/v1/health` is a liveness check (no dependencies).
- `GET /api/v1/health/ready` is a readiness check that pings Postgres, Qdrant and Redis, returning HTTP 503 if any is down.
- Auto docs at `/docs`.

### Challenges
- A readiness check that hangs when a dependency is down. Use short timeouts (1–2 s).
- Don't leak connection strings in health responses.

---

## 10. Task 9 — Logging & Error Handling Skeleton

- Structured JSON logging (`structlog`) with `request_id` per request.
- Middleware that adds `X-Request-ID` and logs method, path, status and latency.
- Custom exception base `AppError` with handlers returning a consistent shape:

```json
{ "error": { "code": "DOCUMENT_NOT_FOUND", "message": "...", "request_id": "..." } }
```

- Reserve a logger channel named `audit` now. In Week 2 it records who asked what and which documents were retrieved. This supports your access-control story.

### Challenges
- Don't log full document text or user queries at INFO level. Both can contain sensitive data.

---

## 11. Task 10 — Code Quality Tooling

`.pre-commit-config.yaml`: ruff (lint + format), end-of-file fixer, trailing whitespace, check-added-large-files (limit 1 MB), detect-private-key, and a custom hook that blocks anything under `data/` from being committed.

```bash
pre-commit install
pre-commit run --all-files
```

### Challenges
- The `check-added-large-files` hook protects you from accidentally committing PDFs and datasets.
- The ruff `S` (security) rules may flag test asserts. Add per-file ignores for `tests/`.

---

## 12. Task 11 — Test Setup

`tests/unit/test_health.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

def test_liveness():
    r = TestClient(app).get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

Also add:
- `tests/conftest.py` with a client fixture.
- An empty `tests/security/test_access_control.py` containing a `pytest.skip("implemented Week 2")` placeholder test named `test_employee_cannot_retrieve_executive_strategy`. The case comes directly from section 15 of your plan, so it stays visible from Day 1.

### Challenges
- Unit tests must not need Docker. Mark anything that does as `@pytest.mark.integration`.

---

## 13. Task 12 — Makefile

```makefile
.PHONY: setup up down logs test lint fmt clean

setup:   ; uv venv --python 3.11 && uv pip install -e ".[dev]" && pre-commit install && cp -n .env.example .env
up:      ; docker compose up -d --build
down:    ; docker compose down
logs:    ; docker compose logs -f api
test:    ; pytest
lint:    ; ruff check . && mypy backend/app
fmt:     ; ruff format . && ruff check --fix .
clean:   ; docker compose down -v
```

### Challenges
- `make clean` deletes volumes, including indexed vectors. Add a warning or confirmation prompt.
- Makefiles need tabs and are awkward on native Windows. Use WSL or provide equivalent `scripts/*.sh`.

---

## 14. Task 13 — CI Pipeline (`.github/workflows/ci.yml`)

Jobs on every PR and push to `develop`/`main`:
1. Checkout, set up Python 3.11, install `.[dev]`.
2. `ruff check .` and `ruff format --check .`
3. `mypy backend/app`
4. `pytest -m "not integration"`
5. (Optional) Build the Docker image to verify the Dockerfile.

### Challenges
- CI will fail if tests depend on `.env` or on services. Provide dummy env vars in the workflow.
- Cache pip/uv to keep CI under 2–3 minutes.

---

## 15. Task 14 — Data Skeleton & Licence Tracking

Create `data/README.md` explaining that data is git-ignored and which script populates each folder.

Create `docs/datasets/DATA_SOURCES.md` with one row per dataset from your plan:

| Dataset | Folder | Source | Licence | Redistribute? | Status |
|---|---|---|---|---|---|
| Synthetic enterprise docs | `data/enterprise_demo/` | Self-generated | Own | Yes (label **synthetic/demo**) | Day 2 |
| SEC EDGAR | `data/sec_edgar/` | sec.gov | Public filings | Verify | Day 2 |
| SQuAD 1.1/2.0 | `data/evaluation/squad/` | rajpurkar.github.io/SQuAD-explorer | Check | Verify | Day 2 |
| HotpotQA | `data/evaluation/hotpotqa/` | Hugging Face | CC BY-SA 4.0 | With attribution + share-alike | Day 2 |
| BEIR SciFact | `data/evaluation/scifact/` | beir-cellar/beir | Check | Verify | Day 2 |
| Natural Questions | `data/evaluation/natural_questions/` | Google Research | Check | Verify | Optional |
| ARAGOG | `data/evaluation/aragog/` | deepset-ai/haystack-evaluation | Check | Verify | Day 2 |
| Enron (optional) | `data/enron/` | CMU | Check; privacy-sensitive | **No** | Optional |

Also create `data/metadata/` placeholders for:
- `documents_metadata.json` (schema from section 14 of your plan: `document_id`, `filename`, `department`, `owner`, `access_level`, `document_type`, `version`, `created_at`, `source`)
- `access_matrix.json` (section 15 roles: employee, manager, admin)

### Challenges
- SEC EDGAR requires a descriptive `User-Agent` header with contact info and rate limiting. Note this for Day 2.
- HotpotQA's CC BY-SA 4.0 means share-alike obligations if you redistribute derived data.
- Enron data contains personal emails. Keep it out of the public repo and the demo.

---

## 16. Task 15 — Documentation Baseline

- **README.md:** project summary, architecture sketch (ASCII is fine), quick start (`make setup && make up`), folder map, roadmap (Week 1–3), and the "synthetic data" disclaimer.
- **ADR-001 (`docs/adr/0001-tech-stack.md`):** record the choices from Section 0 with reasons and consequences. Include the embedding-dimension lock-in note.
- **`docs/architecture/overview.md`:** one diagram of the data flow:

```text
Documents → Parse → Clean → Chunk (+metadata) → Embed → Qdrant + Postgres
User query → AuthN/AuthZ → Filter by access_level → Hybrid retrieve → Rerank → LLM → Answer + citations
                                                                                   ↓
                                                                   Feedback + Evaluation
```

- **`docs/daily_log/day_01.md`:** what was done, problems hit, decisions, next-day plan. Keep one per day; it becomes content for your portfolio write-up.

---

## 17. Task 16 — Commit, PR, Verify

```bash
git add .
git commit -m "chore: project scaffold, folder structure, docker, ci"
git push -u origin feature/day-01-project-setup
# open PR → develop, wait for green CI, squash-merge
git checkout develop && git pull
```

### Fresh-clone verification (important)
```bash
cd /tmp && git clone <repo-url> verify && cd verify
make setup && make up
curl http://localhost:8000/api/v1/health/ready
make test
```

---

## 18. Day 1 Definition of Done

- [ ] Repo created; `main` and `develop` exist; feature branch merged via PR
- [ ] Full folder tree (Section 5) committed, including `data/` layout matching the dataset plan
- [ ] `.env.example` committed; `.env` ignored
- [ ] `docker compose up` starts API, Postgres, Qdrant, Redis
- [ ] `/api/v1/health` and `/api/v1/health/ready` work; `/docs` loads
- [ ] Structured logging with request IDs works
- [ ] `pytest` passes; placeholder access-control test present
- [ ] Pre-commit hooks run; no data files can be committed
- [ ] CI is green on the PR
- [ ] `DATA_SOURCES.md`, ADR-001, README and `day_01.md` written
- [ ] Fresh-clone verification succeeded

---

## 19. Consolidated Challenge List for Day 1

| Challenge | Risk | Mitigation |
|---|---|---|
| Over-engineering the scaffold | Lose half the day | Stubs only; implement features on their scheduled day |
| Environment differences (Windows/Mac/Linux) | "Works on my machine" | Docker for services, Makefile + WSL notes, fresh-clone test |
| Accidentally committing data or secrets | Licence/privacy breach | `.gitignore`, pre-commit large-file and key-detection hooks |
| Embedding dimension lock-in | Full re-index later | Record in ADR and `.env`; make model configurable |
| Hostname mismatch (host vs container) | Connection errors | Separate settings; readiness endpoint |
| Heavy dependencies (torch, unstructured) | Slow setup/CI | Optional extras; install on demand |
| Circular imports | Refactor later | One-way dependency rule documented in architecture doc |
| Port conflicts | Containers fail to start | Configurable host ports |
| Security as an afterthought | Hard to retrofit | `security/`, `retrieval/filters.py`, `tests/security/` created now |

---

## 20. Preview of Day 2

Dataset preparation: generate the synthetic enterprise corpus (PDF/DOCX/XLSX/PPTX) with metadata and the access matrix, download SEC filings (respecting the EDGAR User-Agent and rate rules), and download the evaluation datasets into `data/evaluation/`.
