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

---
### Module 05 — Reciprocal Rank Fusion (RRF)

**Implementation:** LangChain `EnsembleRetriever` using weighted RRF.

**Parameters evaluated:**
- Candidate depth: 20, 50
- BM25 weights: 0.25, 0.50, 0.75
- RRF constant: `c=60`

**Key findings:**
- With 20 candidates per retriever, Query 1's relevant document was missing from the fused candidate set.
- Increasing candidate depth to 50 allowed the relevant document to enter the fused ranking.
- With 50 candidates, the relevant document ranked 37, 69, and 82 for BM25 weights 0.25, 0.50, and 0.75 respectively.
- Increasing semantic weight improved the relevant document's ranking for this particular query.
- None of the configurations placed the relevant document in the final top five.

**Conclusion:** RRF combines rankings effectively, but successful retrieval depends on candidate coverage, fusion weights, and final ranking quality.

Parameter tuning across the full benchmark is deferred to Module 07.
