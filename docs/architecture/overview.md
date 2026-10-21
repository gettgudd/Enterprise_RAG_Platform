# Enterprise RAG Platform — System Architecture & Workflow Blueprint

*Aligned with "Enterprise RAG Platform – Vaibhav" Architecture Plan*

---

## 1. End-to-End Workflow Diagram

The platform follows a 6-stage lifecycle for enterprise knowledge ingestion, query serving, and continuous learning:

```
┌───────────────────┐    ┌────────────────────────┐    ┌──────────────────────┐
│ 1. Document Upload│    │ 2. Document Processing │    │ 3. Query & Retrieval │
│ - PDF             │───►│ - Text Extraction      │───►│ - Natural language   │
│ - Word (DOCX)     │    │ - Clean & Chunk        │    │   question           │
│ - Excel (XLSX)    │    │ - LangChain/LlamaIndex │    │ - Semantic search in │
│ - PPT (PPTX)      │    │   Embeddings           │    │   ChromaDB           │
│ - Single/bulk     │    │ - Store in ChromaDB    │    │ - Top relevant chunks│
└───────────────────┘    └────────────────────────┘    └──────────────────────┘
                                                                   │
                                                                   ▼
┌───────────────────┐    ┌────────────────────────┐    ┌──────────────────────┐
│ 6. Continuous     │    │ 5. Response to User    │    │ 4. LLM Augmentation  │
│    Learning       │    │ - Answer with citations│    │ - Combine context +  │
│ - Feedback triage │◄───│ - Source document refs │◄───│   query              │
│ - KB updates      │    │ - Save chat history    │    │ - LangChain/LlamaIndex│
│ - Fine-tuning     │    │ - Feedback (👍 / 👎)   │    │   with LLM           │
│ - Usage analytics │    │ - Update memory        │    │ - Grounded citations │
└───────────────────┘    └────────────────────────┘    └──────────────────────┘
```

---

## 2. Multi-Tier System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. USERS (Multi-User Access)                                                           │
│ - Employees (Engineering, HR, Finance, etc.)                                           │
│ - Managers (Access Control & Department approvals)                                     │
│ - Administrators (Manage users, permissions, and system indexes)                       │
└───────────────────────────────────────────────────┬────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND LAYER (React Web Application)                                              │
│ - Document Upload Module (PDF, Word, Excel, PPT drag-and-drop)                         │
│ - Chat Interface & Prompt Workspace                                                    │
│ - Chat History Drawer (Track past conversations)                                       │
│ - Feedback Component (Thumbs up / Thumbs down)                                         │
│ - User Management & RBAC Administration                                                │
│ - Dashboard & System Usage Analytics                                                   │
└───────────────────────────────────────────────────┬────────────────────────────────────┘
                                                    │ HTTPS REST APIs
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. BACKEND LAYER (FastAPI)                                                             │
│ - Authentication & Authorization (JWT / OAuth)                                         │
│ - Document Processing APIs (/api/v1/documents)                                         │
│ - RAG / Query APIs (/api/v1/search)                                                    │
│ - Chat History & Feedback APIs (/api/v1/chat, /api/v1/feedback)                        │
│ - User & Permission Management (/api/v1/users)                                         │
│ - Admin APIs (/api/v1/admin) & Dashboard Analytics (/api/v1/analytics)                │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. RAG PIPELINE (LangChain / LlamaIndex Orchestration)                                │
│ 1. Document Ingestion: Parse PDF/Word/Excel/PPT, extract text, clean & chunk           │
│ 2. Embedding Generation: Local sentence-transformers or API embeddings                │
│ 3. Vector Storage: ChromaDB collection indexing with RBAC metadata payload             │
│ 4. Retrieval & Reranking: Semantic search + BM25 keyword fusion + Cross-Encoder rerank │
│ 5. LLM Generation: Grounded prompt augmentation, citation attribution, memory update   │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. DATA & STORAGE LAYER                                                                │
│ - ChromaDB (Vector Database): Document embeddings, chunk texts, and RBAC metadata      │
│ - PostgreSQL 16 (Application Database): Users, permissions, chat history, feedback     │
│ - File Storage (AWS S3): Original raw uploaded documents (PDF, Word, Excel, PPT)       │
│ - Redis 7: Query cache, conversational session state, and ingestion task queue         │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. DEPLOYMENT (AWS Cloud Target)                                                       │
│ - AWS EC2 / ECS: Containerized Backend and Frontend execution                          │
│ - AWS S3: Scalable document blob storage                                               │
│ - AWS RDS (PostgreSQL): Managed relational persistence                                 │
│ - AWS ECR / EKS: Production Docker registry and Kubernetes orchestration               │
│ - AWS CloudFront: Global edge caching for static React assets and CDN distribution     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Cross-Cutting Features Matrix

| Feature | Architectural Component | Implementation |
|---|---|---|
| **Permission Management** | `app/security/rbac.py` & `app/retrieval/filters.py` | Role-based pre-retrieval filtering in ChromaDB (`employee`, `manager`, `admin`). |
| **Multi-user Support** | `app/api/v1/users.py` & `app/security/` | User contexts isolated by team, department, and permission tier. |
| **Chat History** | `app/api/v1/chat.py` & PostgreSQL | Full transcript recording with session tracking and source citations. |
| **Feedback Loop** | `app/api/v1/feedback.py` & PostgreSQL | Thumbs up/down capture and relevance signals for continuous learning. |
| **Memory** | `app/generation/memory.py` | Conversational context retention across multi-turn queries. |
| **Monitoring & Analytics** | `app/api/v1/analytics.py` & `app/core/logging.py` | Latency tracing (`X-Request-ID`), query throughput, and audit logging. |
