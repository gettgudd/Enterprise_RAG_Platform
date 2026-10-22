# Day 2 — Dataset Preparation: Synthetic Enterprise Corpus, SEC EDGAR Filings & Evaluation Benchmarks

**Project:** Enterprise RAG Platform  
**Week 1 / Day 2 of 21**  
**Estimated effort:** 6–8 hours  
**Goal of the day:** At the end of today, the project has a fully populated, verified, and licensed data layer:
1. A multi-format synthetic enterprise corpus (`PDF`, `DOCX`, `XLSX`, `PPTX`) covering 5 core business departments with deterministic Role-Based Access Control (RBAC) tiers.
2. Real-world financial filings (`10-K` / `10-Q`) fetched from SEC EDGAR adhering strictly to the SEC rate limits ($\le 10$ req/s) and User-Agent identification guidelines.
3. Industry-standard retrieval and QA evaluation benchmarks (SQuAD 2.0, HotpotQA, BEIR SciFact, ARAGOG) staged in clean, standardized layouts.
4. A validated metadata catalog (`documents_metadata.json`), access control security matrix (`access_matrix.json`), data integrity validation pipeline, and passing unit test suite.

---

## 0. Day 2 Architectural Context & Design Decisions

In an enterprise Retrieval-Augmented Generation (RAG) system, retrieval accuracy and security are inextricably tied to document characteristics and metadata governance. Day 2 establishes the data foundations that all subsequent pipeline stages (parsing on Day 3, chunking on Day 4, embedding on Day 5, hybrid search on Day 6, and evaluation on Day 7) will consume.

| Component | Technical Choice | Architectural Justification |
|---|---|---|
| **Synthetic Corpus Formats** | PDF, DOCX, XLSX, PPTX | Enterprises operate on diverse document formats, each with distinct layout semantics (tables, slides, headers, paragraphs). |
| **RBAC Classification Tiers** | `public`, `internal`, `confidential`, `restricted` | Mandated by the enterprise security architecture to validate metadata payload filtering and prevent unauthorized data leakage. |
| **Real-World Unstructured Data** | SEC EDGAR Filings (10-K / 10-Q) | Uncurated financial reporting text with dense financial tables, balance sheets, and narrative MD&A sections for realistic testing. |
| **Benchmark QA Datasets** | SQuAD 2.0, HotpotQA, BEIR SciFact, ARAGOG | Provides gold-standard question-context-answer ground truth for offline retrieval benchmarking (Recall@k, MRR, NDCG). |
| **Data Separation Principle** | All raw data git-ignored; code in `scripts/` | Strict compliance with copyright, licensing, and privacy constraints. Repositories stay lightweight and shareable. |

---

## 1. Day 2 Task Overview

| # | Task | Primary Deliverable | Est. Time |
|---|---|---|---|
| 1 | Branching & Day 2 Environment Setup | `feature/day-02-dataset-preparation` branch | 20 min |
| 2 | Metadata Schemas & Access Matrix Formalization | Pydantic schemas in `backend/app/schemas/metadata.py` | 40 min |
| 3 | Multi-Format Synthetic Enterprise Corpus Generator | `scripts/generate_synthetic_docs.py` + docs | 90 min |
| 4 | SEC EDGAR Compliant Downloader with Throttling | `scripts/download_sec_filings.py` + 10-K/10-Q files | 75 min |
| 5 | Benchmark Evaluation Datasets Downloader | `scripts/download_eval_datasets.py` + benchmarks | 60 min |
| 6 | Automated Dataset Integrity & Validation Pipeline | `scripts/validate_datasets.py` | 45 min |
| 7 | Unit & Regression Tests for Dataset Layer | `tests/unit/test_dataset_preparation.py` | 45 min |
| 8 | Licensing, Redistribution & Git Safety Audit | Updated `docs/datasets/DATA_SOURCES.md` & `.gitignore` | 30 min |
| 9 | Documentation Baseline (ADR-002 & Daily Log) | `docs/adr/0002-dataset-strategy.md`, `day_02.md` | 35 min |
| 10 | Verification, PR, Merge to `develop`, Tagging | Tag `day-02-complete` | 20 min |

---

## 2. Task 1 — Git Branching & Ingestion Dependencies

### Features / Actions
Create the dedicated feature branch from the verified `develop` branch:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/day-02-dataset-preparation
```

Verify or install the ingestion and evaluation dependency groups declared in `pyproject.toml`:

```bash
# Using uv or pip
uv pip install -e ".[ingestion,eval,dev]"
# Or standard pip
pip install -e ".[ingestion,eval,dev]"
```

Key libraries leveraged in Day 2:
- `python-docx`: Programmatic generation and inspection of `.docx` files.
- `openpyxl`: Creation of multi-tab `.xlsx` spreadsheets with formulas and cell styles.
- `python-pptx`: Generation of presentation `.pptx` decks with structured slides, titles, and body shapes.
- `reportlab` (or standard Python fallback): Vector-precise `.pdf` generation with tables and headers.
- `httpx`: Async and synchronous HTTP client with connection pooling and retry capabilities.
- `pydantic`: Schema validation and serialization for document catalog records.

### Challenges & Gotchas
- **Missing OS fonts or libraries:** Some PDF libraries rely on native C libraries (like `cairo` or `pango`). Prefer pure-Python libraries (`reportlab`, `pypdf`, `openpyxl`, `python-docx`) that require no external system packages on Windows, macOS, or Linux.
- **Dependency bloat:** Only install `ingestion` and `eval` groups in environments generating or testing datasets. Production API containers do not require generator libraries.

---

## 3. Task 2 — Metadata Schemas & Access Matrix Formalization

### Features / Actions
Every document in an enterprise RAG system must be cataloged with deterministic metadata before parsing and embedding. Define formal Pydantic models for document records and access policies in `backend/app/schemas/metadata.py`.

```python
# backend/app/schemas/metadata.py
from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Department(str, Enum):
    HR = "Human Resources"
    ENGINEERING = "Engineering"
    FINANCE = "Finance"
    LEGAL = "Legal"
    EXECUTIVE = "Executive"
    COMPANY_WIDE = "company-wide"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    HTML = "html"
    TXT = "txt"


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique alphanumeric identifier (e.g., DOC-ENG-001)")
    filename: str = Field(..., description="Original filename with extension")
    department: str = Field(..., description="Business department owner")
    owner: str = Field(..., description="Email address of document owner")
    access_level: AccessLevel = Field(..., description="RBAC security tier")
    document_type: DocumentType = Field(..., description="Format classification")
    version: str = Field(default="1.0", description="Semantic or document version")
    created_at: datetime = Field(..., description="ISO 8601 creation timestamp")
    source: Literal["synthetic", "sec_edgar", "external", "benchmark"] = Field(...)
    description: Optional[str] = Field(default=None, description="Short summary of contents")
    checksum_sha256: Optional[str] = Field(default=None, description="SHA256 hex digest for integrity")


class RolePermission(BaseModel):
    description: str
    allowed_access_levels: List[AccessLevel]
    allowed_departments: List[str]


class AccessMatrix(BaseModel):
    roles: Dict[str, RolePermission]
    sample_users: List[Dict[str, str]]
```

### Done When
- `backend/app/schemas/metadata.py` imports cleanly.
- `data/metadata/documents_metadata.json` and `data/metadata/access_matrix.json` validate against these Pydantic schemas without errors.

---

## 4. Task 3 — Multi-Format Synthetic Enterprise Corpus Generator

### Why Synthetic Enterprise Documents?
1. **Public Portfolio Safety:** Real enterprise data is governed by NDAs. Synthetic data allows 100% public GitHub hosting without privacy or legal liabilities.
2. **Deterministic Evaluation Ground Truth:** By explicitly seeding "needles in a haystack" (exact dates, severance multipliers, budget limits, server architecture decisions), retrieval test suites can test whether the RAG system finds the exact right sentence.
3. **Multi-Format Coverage:** Documents span the 4 major enterprise binary formats (`.pdf`, `.docx`, `.xlsx`, `.pptx`).

### The Document Corpus Specification (12 Documents Across 5 Departments)

| Document ID | Filename | Format | Department | Access Level | Embedded "Needle" Fact |
|---|---|---|---|---|---|
| `DOC-HR-001` | `employee_handbook_2026.pdf` | PDF | Human Resources | `internal` | Standard annual PTO is 22 days; bereavement leave is 5 consecutive business days. |
| `DOC-HR-002` | `benefits_parental_leave_policy.docx` | DOCX | Human Resources | `internal` | Primary caregiver parental leave is 16 fully paid weeks with $5,000 child-care stipend. |
| `DOC-HR-003` | `remote_work_and_equipment_policy.pdf` | PDF | Human Resources | `public` | Home office hardware stipend is $1,200 refreshed every 24 calendar months. |
| `DOC-ENG-001` | `platform_architecture_spec.docx` | DOCX | Engineering | `internal` | ChromaDB vector dimension is 384 with Cosine distance; HNSW M=16, efConstruction=100. |
| `DOC-ENG-002` | `rfc_004_database_migration_plan.pdf` | PDF | Engineering | `confidential` | Zero-downtime PostgreSQL cutover scheduled for Sunday 02:00 UTC using dual-write mode. |
| `DOC-ENG-003` | `production_incident_postmortem_2026_03.docx` | DOCX | Engineering | `internal` | Outage duration was 42 minutes caused by unindexed foreign key in `user_permissions` table. |
| `DOC-FIN-001` | `q4_financial_projections.xlsx` | XLSX | Finance | `confidential` | Projected Q4 SaaS ARR is $24.8M with 81.4% gross margin and 124% net revenue retention. |
| `DOC-FIN-002` | `capex_budget_model_2026.xlsx` | XLSX | Finance | `confidential` | GPU compute cluster allocation capped at $450,000 under project codename "HYPERION". |
| `DOC-FIN-003` | `internal_audit_findings_q1.pdf` | PDF | Finance | `restricted` | Material audit finding: 3 orphan service accounts retained active admin access for 68 days. |
| `DOC-LEG-001` | `master_services_agreement_template.docx` | DOCX | Legal | `internal` | Standard limitation of liability cap is 2x fees paid in the preceding 12-month period. |
| `DOC-LEG-002` | `vendor_security_and_privacy_addendum.pdf` | PDF | Legal | `public` | Vendors must notify enterprise within 24 hours of any confirmed security incident or breach. |
| `DOC-EXEC-001` | `m_and_a_strategy_2026_q3.pptx` | PPTX | Executive | `restricted` | Project "VALKYRIE" acquisition target valuation ceiling is $85M at maximum 6.5x ARR multiple. |
| `DOC-EXEC-002` | `board_of_directors_q2_deck.pptx` | PPTX | Executive | `confidential` | Enterprise expansion targets Tokyo and Frankfurt cloud regions by Q4 2026. |

### Generator Implementation Blueprint (`scripts/generate_synthetic_docs.py`)
The generator must:
1. Support both standard environment execution (with `python-docx`, `openpyxl`, `python-pptx`, `reportlab`) and resilient zero-dependency fallback generation so execution never crashes.
2. Produce authentic binary structures with appropriate file magic headers.
3. Automatically calculate SHA-256 checksums for each generated file.
4. Output the documents to `data/enterprise_demo/{pdf,docx,xlsx,pptx}/`.
5. Sync all records into `data/metadata/documents_metadata.json`.

```bash
# Run the synthetic document generator
python scripts/generate_synthetic_docs.py --output-dir data/enterprise_demo --metadata-path data/metadata/documents_metadata.json
```

---

## 5. Task 4 — SEC EDGAR Compliant Downloader with Throttling

### Features & Compliance Rules
The U.S. Securities and Exchange Commission (SEC) provides public access to corporate filings via the EDGAR system. However, automated scrapers are bound by strict legal and technical requirements:
1. **User-Agent Requirement:** SEC EDGAR explicitly blocks requests missing a descriptive `User-Agent` formatted as: `Sample Company Name AdminContact@<sample company domain>.com`.
2. **Rate Limit:** SEC imposes a maximum limit of **10 requests per second**. Exceeding this rate triggers an automatic IP-based HTTP 429 / connection rejection.
3. **Throttling Implementation:** The downloader must incorporate a token-bucket rate limiter or a deterministic delay (e.g., minimum 150ms between requests) plus exponential backoff on HTTP 429 / 503 responses.

### Target Companies and Filings

| Company | CIK (Central Index Key) | Ticker | Target Filing Types | Target Years |
|---|---|---|---|---|
| **Apple Inc.** | `0000320193` | `AAPL` | `10-K` (Annual), `10-Q` (Quarterly) | 2024 / 2025 |
| **Microsoft Corp.** | `0000789019` | `MSFT` | `10-K` (Annual), `10-Q` (Quarterly) | 2024 / 2025 |
| **NVIDIA Corp.** | `0001045810` | `NVDA` | `10-K` (Annual), `10-Q` (Quarterly) | 2024 / 2025 |

### Storage Organization
```text
data/sec_edgar/
├── company_01/                 # Apple (AAPL)
│   ├── AAPL_10K_2024.txt
│   ├── AAPL_10Q_2024_Q3.txt
│   └── metadata.json
├── company_02/                 # Microsoft (MSFT)
│   ├── MSFT_10K_2024.txt
│   └── metadata.json
└── company_03/                 # NVIDIA (NVDA)
    ├── NVDA_10K_2024.txt
    └── metadata.json
```

### Execution Command
```bash
python scripts/download_sec_filings.py \
  --companies AAPL,MSFT,NVDA \
  --forms 10-K,10-Q \
  --user-agent "EnterpriseRAGPlatform/1.0 (compliance@enterprise-rag.internal)" \
  --output-dir data/sec_edgar \
  --rate-limit 5.0
```

---

## 6. Task 5 — Benchmark Evaluation Datasets Downloader & Normalizer

### Benchmark Datasets Rationale
To benchmark RAG retrieval precision without bias before evaluating custom enterprise queries on Day 7, we stage standard NLP and IR corpora:

| Dataset | Purpose in RAG Evaluation | Structure / Splits | Staging Directory |
|---|---|---|---|
| **SQuAD 2.0** | Extractive question-answering precision + detecting unanswerable questions. | `dev-v2.0.json` (11,873 questions, contexts, answers) | `data/evaluation/squad/` |
| **HotpotQA** | Multi-hop reasoning across multiple documents; tests whether retriever gathers disjoint facts. | `hotpot_dev_distractor_v1.json` | `data/evaluation/hotpotqa/` |
| **BEIR SciFact** | Domain-specific claim verification; tests dense vs BM25 keyword hybrid retrieval. | `corpus.jsonl`, `queries.jsonl`, `qrels/test.tsv` | `data/evaluation/scifact/` |
| **ARAGOG** | Advanced retrieval and hallucination mitigation benchmark from haystack/deepset. | `aragog_sample.jsonl` | `data/evaluation/aragog/` |

### Resilience & Offline Fallbacks
Network downloads from Hugging Face or public mirrors can occasionally encounter DNS issues, timeouts, or rate limits. The downloader `scripts/download_eval_datasets.py` includes built-in offline benchmark fixtures so test environments and CI runners are guaranteed to succeed even without internet connectivity.

```bash
python scripts/download_eval_datasets.py \
  --datasets squad,hotpotqa,scifact,aragog \
  --output-dir data/evaluation \
  --sample-only
```

---

## 7. Task 6 — Automated Dataset Integrity & Validation Pipeline

### Features / Actions
Create `scripts/validate_datasets.py` to verify:
1. **File Presence:** Every document listed in `data/metadata/documents_metadata.json` exists on disk.
2. **Binary Header Verification:**
   - PDF files begin with `%PDF-` magic header.
   - DOCX, XLSX, and PPTX files start with the PK Zip archive header `\x50\x4B\x03\x04`.
   - JSON files parse cleanly with valid UTF-8.
3. **Checksum Verification:** SHA-256 hashes match records in the metadata catalog.
4. **Access Matrix Consistency:** Every `access_level` and `department` tagged in documents matches valid tiers in `data/metadata/access_matrix.json`.
5. **Git Cleanliness:** Scans the Git index to guarantee no raw data files are accidentally staged.

```bash
python scripts/validate_datasets.py --check-all
```

---

## 8. Task 7 — Unit & Regression Tests for Dataset Layer

Author `tests/unit/test_dataset_preparation.py` covering:
- Document metadata schema parsing and validation.
- Role-Based Access Control matrix structure.
- Synthetic document generator output validation.
- SEC EDGAR rate-limiting token bucket tests.
- Benchmark sample loader tests.

Run tests:
```bash
pytest tests/unit/test_dataset_preparation.py -v
```

---

## 9. Task 8 — Licensing, Redistribution & Git Safety Audit

Review and update `docs/datasets/DATA_SOURCES.md`:
1. Record verified licenses for all corpora:
   - Synthetic Enterprise Corpus: **MIT / CC0** (Free redistribution).
   - SEC EDGAR Filings: **Public Domain** (US Government work).
   - SQuAD 2.0: **CC BY-SA 4.0** (Attribution required).
   - HotpotQA: **CC BY-SA 4.0** (Attribution required).
   - BEIR SciFact: **Apache-2.0** (Permissive).
   - ARAGOG: **Apache-2.0 / CC BY-SA**.
2. Audit `.gitignore`:
   ```bash
   git status --ignored
   # Ensure all files under data/enterprise_demo, data/sec_edgar, and data/evaluation are ignored!
   ```

---

## 10. Task 9 — Documentation Baseline (ADR-002 & Daily Log)

- **ADR-002 (`docs/adr/0002-dataset-strategy.md`):** Record the rationale for synthetic enterprise documents, the multi-format matrix, SEC rate limit compliance, and offline evaluation benchmark splits.
- **`docs/daily_log/day_02.md`:** Summary of completed tasks, metrics, challenge mitigations, and the plan for Day 3.

---

## 11. Task 10 — Commit, PR, Verification & Tagging

```bash
git add docs/adr/0002-dataset-strategy.md \
        docs/daily_log/day_02.md \
        docs/datasets/DATA_SOURCES.md \
        backend/app/schemas/metadata.py \
        scripts/generate_synthetic_docs.py \
        scripts/download_sec_filings.py \
        scripts/download_eval_datasets.py \
        scripts/validate_datasets.py \
        tests/unit/test_dataset_preparation.py \
        day_02_dataset_preparation.md

git commit -m "feat(data): implement Day 2 dataset preparation, synthetic generator, sec edgar downloader, and validation suite"
git push -u origin feature/day-02-dataset-preparation

# Open PR into develop, verify tests pass, squash-merge, and tag:
git checkout develop
git pull origin develop
git tag -a day-02-complete -m "Day 2 Complete: Dataset preparation and validation suite"
git push origin day-02-complete
```

---

## 12. Day 2 Definition of Done

- [ ] `feature/day-02-dataset-preparation` branch created and active.
- [ ] Pydantic metadata and access matrix schemas defined in `backend/app/schemas/metadata.py`.
- [ ] `scripts/generate_synthetic_docs.py` generates at least 12 multi-format documents across PDF, DOCX, XLSX, and PPTX with embedded evaluation needle facts.
- [ ] `data/metadata/documents_metadata.json` updated with accurate IDs, paths, departments, access levels, and checksums.
- [ ] `scripts/download_sec_filings.py` implemented with SEC-compliant User-Agent header and deterministic rate-limiting ($\le 10$ req/s).
- [ ] `scripts/download_eval_datasets.py` stages SQuAD 2.0, HotpotQA, BEIR SciFact, and ARAGOG with offline fallback support.
- [ ] `scripts/validate_datasets.py` passes all verification checks (checksums, magic headers, RBAC tags, git cleanliness).
- [ ] Unit test suite in `tests/unit/test_dataset_preparation.py` passes with 100% success.
- [ ] `docs/datasets/DATA_SOURCES.md` updated with complete licensing information.
- [ ] ADR-002 and `docs/daily_log/day_02.md` committed.
- [ ] Working tree clean; no binary datasets staged in Git.

---

## 13. Consolidated Challenge List for Day 2

| Challenge | Risk | Mitigation |
|---|---|---|
| **Binary document generation dependencies** | Missing C-libraries or system fonts cause PDF/DOCX generation to fail. | Built-in fallback generator in `scripts/generate_synthetic_docs.py` using pure Python byte structures and standard libraries. |
| **SEC EDGAR HTTP 429 blocks** | Automated scrapers get blacklisted by the SEC. | Enforce custom User-Agent with contact email, limit rate to $\le 5$ req/s, and add exponential backoff. |
| **Accidental git commit of large corpora** | Repository bloat and potential licensing violations. | Tested `.gitignore` rules; `scripts/validate_datasets.py` scans `git status` for untracked/staged files. |
| **Flaky benchmark downloads** | External download servers fail or time out during CI/CD. | Built-in offline fallback fixtures for SQuAD, HotpotQA, SciFact, and ARAGOG. |
| **RBAC tag drift** | Documents assigned departments or access levels that don't match the access matrix. | Pydantic schema validation strictly enums all valid tiers (`public`, `internal`, `confidential`, `restricted`). |

---

## 14. Preview of Day 3

**Day 3 — Document Parsing, Extraction & Multimodal Normalization:**  
Implementing dedicated parsers for each format (`pdfplumber` / `pypdf` for PDF, `python-docx` for Word, `openpyxl` for Excel spreadsheets, and `python-pptx` for presentations), extracting structured text, headers, and tables, and normalizing all content into unified `ParsedDocument` intermediate representations.
