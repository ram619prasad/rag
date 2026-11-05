# Project 03 — Smart Search & Retrieval Engineering

## Objective

Build and evaluate keyword, semantic, and hybrid retrieval using a consistent benchmark dataset.

## Dataset

- Name: BEIR SciFact
- Corpus: 5,183 scientific abstracts
- Queries: Scientific claims
- Ground truth: Official train and test relevance judgments

## Planned Modules

1. Dataset Preparation
2. BM25 Retrieval
3. Dense Semantic Retrieval
4. Hybrid Search
5. Reciprocal Rank Fusion
6. Metadata Filtering
7. Retrieval Evaluation
8. End-to-End Comparison

## Module 01 — Dataset Preparation

- Download the official SciFact benchmark.
- Load corpus, queries, and relevance judgments.
- Verify ground-truth references.
- Inspect a sample query and relevant document.

---

### Module 04 — Hybrid Retrieval

**Implementation:** LangChain `EnsembleRetriever` combining BM25 and Chroma semantic retrieval with equal weights and weighted Reciprocal Rank Fusion.

**Experiment results (Top 5):**

| Query | BM25 Recall | Semantic Recall | Hybrid Recall |
|---|---|---|---|
| 1 | 0.0 | 0.0 | 0.0 |
| 1303 | 1.0 | 1.0 | 1.0 |

**Key findings:**
- Hybrid retrieval successfully combines keyword and semantic candidates.
- Hybrid retrieval did not improve Recall@5 on these two sample queries.
- Candidate coverage limits fusion: a relevant document missing from both candidate sets cannot be promoted by RRF.
- Larger candidate sets and fusion-weight experiments are deferred to Module 05.
