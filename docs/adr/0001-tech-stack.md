# ADR 0001: Core Technology Stack & Architecture Choices

- **Status:** Accepted
- **Date:** 2026-10-21
- **Deciders:** Architecture Team (Aligned with "Enterprise RAG Platform – Vaibhav" Plan)
- **Context:** Enterprise RAG Platform

## Context and Problem Statement
We require an enterprise-grade Retrieval-Augmented Generation (RAG) platform capable of ingesting diverse corporate knowledge files (PDF, Word, Excel, PowerPoint), enforcing role-based access control (RBAC), performing hybrid search (semantic + lexical), managing multi-turn chat memory with citations, and deploying onto AWS cloud infrastructure.

## Decision Drivers
1. **Architectural Plan Alignment:** Exact adherence to the multi-tier system architecture and 6-stage workflow diagram (Document Upload, Processing, Query & Retrieval, LLM Augmentation, Response to User, Continuous Learning).
2. **Vector Storage:** Direct adoption of **ChromaDB** for vector embeddings and chunk metadata storage.
3. **Blob Storage:** Direct adoption of **AWS S3** for raw document archiving (with local storage fallback for offline dev).
4. **Relational Storage:** **PostgreSQL 16** for users, permissions, chat history, and user feedback.
5. **Orchestration:** **FastAPI** backend with **LangChain / LlamaIndex** integration.
6. **Frontend:** **React** web application for upload, chat, user management, and analytics dashboards.

## Technology Decisions

| Architectural Tier | Technology Choice | Rationale | Alternatives Evaluated |
|---|---|---|---|
| **Primary Vector DB** | **ChromaDB** | Primary vector store specified in architectural plan; lightweight, native metadata filtering, embedded or client/server mode. | Qdrant (maintained as optional secondary backend), Pinecone, Weaviate. |
| **Relational Database** | **PostgreSQL 16** | Application database for users, permissions, chat history, and user feedback (thumbs up/down). | MySQL, MongoDB. |
| **Document Blob Storage** | **AWS S3** | Durable object storage for original uploaded PDF, Word, Excel, and PPT files; configurable for local dev. | Local disk only, Google Cloud Storage. |
| **API Framework** | **FastAPI** | High-performance async Python framework, automatic OpenAPI documentation, Pydantic v2 schemas. | Flask, Django REST framework. |
| **RAG Orchestration** | **LangChain / LlamaIndex** | Industry standard RAG pipelines, chunking, embedding generation, and prompt augmentation. | Pure native SDK scripting. |
| **Frontend Framework** | **React** | Interactive web UI for document upload, chat interface, history drawer, and analytics dashboard. | Vue, Svelte, Next.js. |
| **Cache & Task Queue** | **Redis 7** | Sub-millisecond session state, query caching, and async ingestion queue. | Memcached. |
| **Cloud Target** | **AWS (ECS, S3, RDS, CloudFront)** | Specified target cloud architecture for containerized production deployment. | GCP, Azure. |

## Architectural Consequences & Constraints

### ⚠️ Embedding Dimension Consistency
- The default embedding model is `BAAI/bge-small-en-v1.5` (384 dimensions).
- ChromaDB collections must be configured to match the embedding model dimensions. Changes to embedding models require re-indexing existing collections.

### Pre-Retrieval RBAC Enforcement
- ChromaDB metadata queries apply `$in` and `$and` clauses on `access_level` and `department` prior to returning results to ensure employees cannot access confidential or restricted documents.
