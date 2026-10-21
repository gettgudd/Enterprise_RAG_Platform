# Data Directory

This directory contains corpora, filings, and evaluation datasets used by the Enterprise RAG Platform.

## ⚠️ Important Git Guidelines
- **All raw and processed data in this folder is GIT-IGNORED** (except metadata placeholders and `.gitkeep` files).
- Never commit actual PDF, DOCX, XLSX, PPTX, or dataset files to GitHub.
- Datasets are populated via dedicated scripts in `scripts/`.

## Directory Structure & Population Scripts

| Subdirectory | Purpose | Populated By | Schedule |
|---|---|---|---|
| `enterprise_demo/` | Synthetic corporate documents (PDF, DOCX, XLSX, PPTX) across HR, Legal, Eng, Finance, Exec | `scripts/generate_synthetic_docs.py` | Day 2 |
| `sec_edgar/` | Real SEC 10-K/10-Q financial filings from 3 public companies | `scripts/download_sec_filings.py` | Day 2 |
| `evaluation/` | Benchmark QA & retrieval datasets (SQuAD, HotpotQA, BEIR SciFact, ARAGOG) | `scripts/download_eval_datasets.py` | Day 2 |
| `enron/` | Optional email corpus for advanced search benchmarks (privacy sensitive — do not redistribute) | Manual download | Optional |
| `metadata/` | Document metadata catalogs and ACL permission matrices | Committed JSON schemas | Day 1+ |
| `processed/` | Cleaned text representations and chunk JSONL artifacts | `scripts/ingest_corpus.py` | Day 4 |
| `eval_internal/` | Converted internal evaluation benchmark records | `scripts/run_eval.py` | Day 7 |
