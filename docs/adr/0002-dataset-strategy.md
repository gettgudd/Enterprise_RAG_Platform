# ADR-002: Dataset Strategy — Synthetic Enterprise Corpus, SEC EDGAR Filings & Evaluation Benchmarks

- **Status:** Accepted
- **Date:** 2026-10-22
- **Deciders:** Core Platform & AI Architecture Team
- **Context:** Day 2 of 21 (Week 1)

---

## 1. Context and Problem Statement

An enterprise Retrieval-Augmented Generation (RAG) platform must handle diverse multi-modal document structures (PDF, Word, Excel, PowerPoint), enforce strict Role-Based Access Control (RBAC) filtering, and provide objective metrics on retrieval accuracy (Recall@k, MRR, NDCG).

However, using real proprietary corporate documents introduces severe risks:
1. **Confidentiality / NDA Breach:** Internal corporate intellectual property and employee PII cannot be committed to open repositories or public portfolios.
2. **Ambiguous Retrieval Ground Truth:** Real documents lack deterministic "needle in a haystack" test cases, making automated retrieval regression testing difficult.
3. **Format Heterogeneity:** Real enterprise document lakes are messy, requiring structured parsers across tables, balance sheets, slides, and legal paragraphs.

We need a comprehensive dataset strategy that enables public open-source demonstration, zero privacy liability, rigorous RBAC validation, and reproducible offline evaluation.

---

## 2. Decision Drivers

- **Zero Data Privacy Liability:** Code and documentation must be 100% shareable on public GitHub.
- **Multi-Format Coverage:** Must exercise parsing across PDF, DOCX, XLSX, and PPTX.
- **Deterministic Evaluation Needles:** Exact factual statements embedded in specific documents to test semantic and keyword retrieval precision.
- **Real-World Unstructured Data:** Real 10-K/10-Q SEC EDGAR filings to test financial table parsing and long-document dense retrieval.
- **Gold-Standard Benchmarks:** Standardized SQuAD 2.0, HotpotQA, BEIR SciFact, and ARAGOG splits for unbiased retrieval benchmarking.

---

## 3. Considered Options

1. **Option 1: Crawl Public Internet / Web Scrapes**  
   *Pros:* Abundant raw text.  
   *Cons:* Uncurated, lack of document formats (mostly HTML), no embedded RBAC tiers, no deterministic QA pairs.
2. **Option 2: Use Public Enron Email Corpus Only**  
   *Pros:* Real enterprise communication.  
   *Cons:* Contains real employee names and personal emails; ethically sensitive; exclusively plaintext/email format without tables, slides, or spreadsheets.
3. **Option 3 (Chosen): Hybrid Three-Pillar Dataset Strategy**  
   - **Pillar A: Multi-Format Synthetic Enterprise Corpus (`data/enterprise_demo/`):** 13 curated documents spanning 5 business departments (HR, Engineering, Finance, Legal, Executive) across PDF, DOCX, XLSX, and PPTX with explicit RBAC classification tags (`public`, `internal`, `confidential`, `restricted`) and ground-truth evaluation needles.
   - **Pillar B: SEC EDGAR Filings (`data/sec_edgar/`):** Authentic 10-K / 10-Q filings for Apple, Microsoft, and NVIDIA fetched under SEC-compliant rate limiting ($\le 10$ req/s) with descriptive User-Agent headers.
   - **Pillar C: Standard Evaluation Benchmarks (`data/evaluation/`):** Standardized local splits of SQuAD 2.0, HotpotQA, BEIR SciFact, and ARAGOG.

---

## 4. Decision Outcome

**Chosen Option: Option 3 (Hybrid Three-Pillar Dataset Strategy)**.

### Positive Consequences
- **Complete Legal Safety:** Synthetic documents are self-authored under MIT / CC0 licensing; SEC filings are in the public domain.
- **Comprehensive Format Testing:** Prepares Day 3 parsers for PDF layouts, Word headers, Excel spreadsheet cells, and PowerPoint bullet cards.
- **Deterministic RBAC Verification:** Allows unit and security tests to assert that employees cannot retrieve confidential or restricted documents.
- **CI/CD Determinism:** Built-in offline fixtures ensure tests and ingestion pipelines execute reliably without external network dependencies.

### Negative Consequences / Trade-offs
- Synthetic documents require continuous manual expansion to cover novel linguistic edge cases.
- SEC EDGAR scraping requires strict rate-limiting compliance to prevent IP bans.

---

## 5. Compliance and Data Governance Rules

1. All raw corpora in `data/` remain strictly **git-ignored**.
2. Document catalog records are tracked in version-controlled JSON schema: `data/metadata/documents_metadata.json`.
3. Every document must be assigned an immutable `document_id`, `access_level`, `department`, and SHA-256 checksum.
