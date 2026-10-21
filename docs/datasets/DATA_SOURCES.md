# Data Sources & Licensing Registry

This document records the provenance, licensing terms, and redistribution compliance status for all corpora and benchmarks used in the Enterprise RAG Platform.

## Dataset Inventory

| Dataset | Folder | Source | Licence | Redistribute? | Status | Notes |
|---|---|---|---|---|---|---|
| Synthetic enterprise docs | `data/enterprise_demo/` | Self-generated | MIT / Own Work | **Yes** (label as **synthetic/demo**) | Day 2 | Generated across PDF, DOCX, XLSX, PPTX with RBAC access levels |
| SEC EDGAR | `data/sec_edgar/` | sec.gov | Public Filings | Verify | Day 2 | Must adhere to SEC `User-Agent` and 10 req/s rate limits |
| SQuAD 1.1/2.0 | `data/evaluation/squad/` | rajpurkar.github.io/SQuAD-explorer | CC BY-SA 4.0 | Verify / Attribution | Day 2 | Standard extractive QA evaluation benchmark |
| HotpotQA | `data/evaluation/hotpotqa/` | Hugging Face / hotpotqa.github.io | CC BY-SA 4.0 | With attribution + share-alike | Day 2 | Multi-hop reasoning benchmark |
| BEIR SciFact | `data/evaluation/scifact/` | beir-cellar/beir | Apache-2.0 | Verify | Day 2 | Domain-specific biomedical/scientific claim verification |
| Natural Questions | `data/evaluation/natural_questions/` | Google Research | CC BY-SA 3.0 | Check / Verify | Optional | Real user Google queries with long/short answer annotations |
| ARAGOG | `data/evaluation/aragog/` | deepset-ai/haystack-evaluation | Apache-2.0 / CC | Verify | Day 2 | Advanced retrieval evaluation benchmark |
| Enron Email Corpus | `data/enron/` | CMU | Research Only | **NO** | Optional | Contains personal employee emails. Kept out of public repositories. |

## Redistribution and Privacy Rules
1. **Never commit raw data:** All paths in `data/` are git-ignored except `.gitkeep` and metadata definitions.
2. **Clear synthetic labeling:** Any published demo artifacts originating from `data/enterprise_demo/` must be labeled as synthetic.
3. **Attribution:** Any derived evaluation splits must maintain original author attribution and license notices according to CC BY-SA 4.0 guidelines.
