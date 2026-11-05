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

---

### Module 06 — Metadata Filtering

**Implementation:** Chroma metadata filtering using `$in`.

**Experiment:**
- Unfiltered search: 5 results from 5,183 eligible documents.
- Filtered search: 3 results from 3 eligible documents.
- Verified that filtered results contained only the allowed document IDs.

**Key findings:**
- Metadata filtering restricts which documents are eligible for semantic retrieval.
- Chroma applies the filter as part of retrieval.
- Filtering before top-K selection avoids losing eligible documents that would otherwise be outside the unfiltered top K.
- Metadata filters do not modify document embeddings.

---

## Project 03 — Final Results

**Status:** Completed (learning scope)

### Implemented

- SciFact dataset preparation and validation (5,183 documents)
- BM25 keyword retrieval
- Dense semantic retrieval with OpenAI embeddings and Chroma
- Hybrid retrieval using LangChain EnsembleRetriever
- Weighted Reciprocal Rank Fusion
- Chroma metadata filtering
- Retrieval evaluation using ir-measures
- Reproducible benchmark integration

### Benchmark Configuration

- Dataset: BEIR SciFact
- Evaluation split: Train
- Queries: 20 (deterministic random sample, seed 42)
- Embedding model: text-embedding-3-small
- Hybrid weights: BM25 0.5, Semantic 0.5
- RRF constant: 60
- Candidate depth: 20 per retriever

### Results

| Metric | BM25 | Semantic | Hybrid |
|---|---:|---:|---:|
| Recall@5 | 0.6750 | 0.9250 | 0.8000 |
| Recall@10 | 0.7000 | 0.9250 | 0.9500 |
| Precision@10 | 0.0800 | 0.1000 | 0.1050 |
| RR@10 | 0.6125 | 0.7517 | 0.7035 |
| nDCG@10 | 0.6383 | 0.7930 | 0.7605 |

### Key Learnings

1. BM25 and dense retrieval have complementary strengths.
2. Semantic retrieval achieved the best early-ranking quality in our sample.
3. Hybrid retrieval achieved the highest Recall@10.
4. RRF can improve or degrade rankings depending on query characteristics and fusion settings.
5. Metadata filtering restricts the eligible search space before ranking.
6. Retrieval quality should be measured using ground-truth relevance judgments.

### Limitations

- Results are based on only 20 training queries.
- RRF weights were not systematically optimized.
- Full 300-query held-out test evaluation was deferred.
- Latency, cost, and production-scale performance were not benchmarked.

### Reproduce

```bash
uv run 07_retrieval_evaluation.py
```

Requires the downloaded SciFact dataset, existing Chroma index, and configured OpenAI API key.