# RAG Engineering — Learning & Portfolio Roadmap

A hands-on, project-based journey to **master Retrieval-Augmented Generation (RAG)**: from a minimal working application to an evaluated, secure, production-oriented system.

The goal is not to collect implementations of fashionable techniques. It is to understand **why** each technique exists, identify the failure it addresses, implement and measure it, and decide when its complexity is justified.

## Repository organization

The `rag/` folder is a **local workspace**, not a shared Python package or a monorepo. Each numbered directory is an **independent, runnable project** with its own Git repository, `pyproject.toml`, `uv.lock`, environment, dataset setup, evaluation commands, and README. No project may depend on source code imported from a sibling project.

```text
rag/
├── README.md                       # Portfolio roadmap (this file)
├── 00-minimal-rag/                 # A complete, simple RAG baseline
├── 01-document-engineering/       # Ingestion and document quality
├── 02-chunking-engineering/       # Chunk boundaries and information preservation
├── 03-retrieval-foundations/      # Embeddings, BM25, semantic and hybrid search
├── 04-advanced-retrieval/         # Contextual, parent-child and hierarchical retrieval
├── 05-query-intelligence/         # Query transformation and retrieval decisions
├── 06-grounded-generation/       # Reranking, context assembly and grounded answers
└── 07-production-rag/             # Reliable, secure, observable end-to-end service
```

> The tree shows the **planned final structure**. Create one project when starting it; do not generate empty folders or future scaffolding upfront. Each project can be cloned, installed, run, and evaluated on its own.

## Projects at a glance

| Project | Purpose | Primary outcome |
|---|---|---|
| **00 — Minimal RAG** | Build a small end-to-end pipeline without unnecessary abstractions | A question-answering application with citations and a measured baseline |
| **01 — Document Engineering** | Ingest real documents reliably and preserve useful structure | A reproducible, provenance-aware ingestion pipeline |
| **02 — Chunking Engineering** | Understand how chunk boundaries affect retrieval and answers | A controlled comparison of chunking strategies |
| **03 — Retrieval Foundations** | Master lexical, vector and hybrid evidence search | Benchmarked retrievers and justified ranking choices |
| **04 — Advanced Retrieval** | Explore retrieval architectures for context and document structure | Evidence-based comparisons of advanced strategies |
| **05 — Query Intelligence** | Handle difficult, ambiguous and multi-hop questions | Measured query transformation and routing workflows |
| **06 — Grounded Generation** | Convert retrieved evidence into accurate, attributable answers | A reranked, context-budgeted answer pipeline evaluated for grounding |
| **07 — Production RAG** | Integrate proven components and meet operational requirements | A deployed, testable RAG service with observability and safeguards |

---

## 00 — Minimal RAG

**Problem:** Build something complete before optimizing individual parts. A simple working system makes later improvements measurable.

**Focus topics**
- RAG mental model: ingestion → chunking → embedding → retrieval → augmentation → generation.
- Basic document loading, fixed-size splitting, embedding, and Chroma vector search.
- Prompt construction with retrieved source passages.
- LLM answer generation, source IDs/citations, and a clear *not enough evidence* response.
- Inspecting retrieved passages, simple failure cases, tokens, cost, and latency.
- Tiny manually reviewed evaluation set and baseline answer quality.

**Deliverable:** Independently runnable CLI or small app that answers questions from a limited technical-document corpus and displays supporting sources.

**Mastery check:** Explain the complete data flow and diagnose a wrong answer without changing several components at once.

## 01 — Document Engineering

**Problem:** Retrieval cannot recover information that ingestion lost or corrupted.

**Focus topics**
- Text, Markdown, HTML, DOCX and PDF loading; document structure and normalization.
- PDFs with columns, tables, headers/footers, and complex layouts; scanned PDFs and OCR limitations.
- Metadata, source provenance, canonical identifiers, stable document IDs and versioning.
- Error handling, validation, deduplication, document parsing quality and batch ingestion.
- Incremental ingestion concepts; detecting added, changed, and removed documents.
- Focused multimodal/layout-aware extraction lab for tables and images where text extraction is insufficient.

**Deliverable:** Reproducible ingestion workflow over a small collection of varied real documents with an extraction-quality report.

**Mastery check:** Identify which extraction choices cause lost meaning or bad downstream retrieval.

## 02 — Chunking Engineering

**Problem:** Arbitrary chunk boundaries can separate definitions, formulas, examples, tables and their explanations.

**Focus topics**
- Fixed-size and recursive chunking; chunk size and overlap trade-offs.
- Token-aware vs character-aware splitting; tokenization and context-window budgets.
- Structure-aware chunking using Markdown headings, sections, tables, and code blocks.
- Semantic chunking and coherent topic boundaries.
- Adaptive chunking: choosing splitting strategies based on document characteristics.
- Late chunking: concept, embedding-model requirements and a focused demonstration if practical.
- Chunk metadata, parent relationships, boundary failures, duplication and context completeness.
- Controlled comparisons: retrieval accuracy, evidence coverage, chunk-length distributions, token cost and downstream answer effects.

**Deliverable:** Benchmarked chunking strategies on the **same frozen source documents and questions**, with documented trade-offs.

**Mastery check:** Given a failed retrieval, show whether the chunk boundary caused the failure and demonstrate a targeted fix.

## 03 — Retrieval Foundations

**Problem:** A vector search alone does not consistently find every kind of evidence.

**Focus topics**
- Embedding fundamentals and model selection; dimensionality, normalization and similarity metrics (cosine, dot product, distance).
- Exact vs approximate nearest-neighbor search; HNSW intuition, indexing and latency/recall trade-offs.
- Lexical search: tokenization, inverted indexes, TF-IDF intuition and BM25.
- Dense/semantic retrieval and metadata filtering.
- Hybrid retrieval, rank fusion (RRF), weighting and candidate-set construction.
- Retrieval metrics: Recall@K, MRR, nDCG; relevance judgments, query splits and per-query error analysis.
- Embedding/index costs, retrieval latency, and reproducible experiment configuration.

**Deliverable:** Independently runnable BM25, semantic and hybrid baselines evaluated on a benchmark with established relevance labels.

**Mastery check:** Explain and debug when lexical search beats semantic search (and vice versa), and defend a hybrid ranking strategy.

## 04 — Advanced Retrieval

**Problem:** Even a strong basic retriever may miss context, return incomplete passages, or ignore document structure.

**Focus topics**
- Contextual retrieval: document-aware chunk enrichment, contextual embeddings and contextual BM25.
- Parent-child retrieval: search smaller units, return larger parent context; parent storage and deduplication.
- Hierarchical retrieval: document → section → passage; top-down search and error propagation.
- Multi-stage retrieval, candidate selection, diversity, metadata-aware retrieval and context expansion.
- Controlled architecture comparisons: recall, rank quality, context returned, tokens, latency and cost.
- RAPTOR / recursive summaries as a **conceptual or optional advanced lab**, not mandatory infrastructure.

**Deliverable:** A benchmarked set of retrieval architectures with an explicit choice for when each is useful.

**Mastery check:** Recommend or reject an advanced strategy based on a real failure case and measured benefit—not novelty.

## 05 — Query Intelligence

**Problem:** Poorly expressed, ambiguous or multi-part questions can fail even with a good index.

**Focus topics**
- Query intent classification, ambiguity and query-type-driven strategies.
- Query rewriting, expansion, multi-query retrieval and result deduplication/fusion.
- Query decomposition for multi-hop or cross-document questions; evidence aggregation.
- HyDE (Hypothetical Document Embeddings): mechanism, assumptions and failure cases.
- Query routing across indexes, retrievers or structured vs unstructured sources.
- Selective retrieval, confidence heuristics and corrective/retry flows.
- Evaluation of effectiveness vs added LLM calls, latency and cost.

**Deliverable:** An evaluated query-intelligence layer that applies transformations **only when they are justified**.

**Mastery check:** Identify when rewriting or decomposition helps, harms, or adds cost without benefit.

## 06 — Grounded Generation

**Problem:** Retrieving relevant text is not the same as producing an accurate, supported answer.

**Focus topics**
- First-stage retrieval vs cross-encoder/LLM reranking and relevance-aware selection.
- Contextual compression, redundancy removal, context ordering and token-budget allocation.
- Prompt augmentation, instruction/evidence separation and long-context trade-offs.
- Grounded answer generation, claim-to-source citations and citation verification.
- Conflicting evidence, insufficient evidence, calibrated abstention and corrective retrieval handoff.
- RAG evaluation: answer correctness, relevance, faithfulness, context precision/recall, citation support.
- DeepEval for LLM/RAG quality; retain deterministic retrieval metrics when appropriate.
- Human review, LLM-as-judge limitations, evaluation variability, latency and cost.

**Deliverable:** A cited answer-generation pipeline with retrieval/reranking ablations and an answer-quality evaluation report.

**Mastery check:** Given an ungrounded answer, distinguish missing retrieval evidence from poor context assembly or generation.

## 07 — Production RAG

**Problem:** A good demo is not yet a reliable, safe or maintainable system.

**Focus topics**
- End-to-end design and selective integration of techniques that actually improved quality.
- FastAPI interfaces, async workflows, streaming, timeouts, retries and graceful degradation.
- Durable stores, incremental updates/deletes, index freshness, versioning and embedding migrations.
- Authentication, authorization, document-level access control and tenant isolation.
- Prompt-injection defenses, untrusted retrieved documents, sensitive-data handling and source provenance.
- Observability: tracing, retrieval diagnostics, quality monitoring, cost and token accounting.
- Performance: caching, batching, concurrency, p95/p99 latency, rate limits and scaling.
- Operational evaluation, regression suites, failure injection, deployment and reproducibility.
- Architecture decisions: vector vs hybrid vs hierarchical retrieval; long-context vs retrieval; reliability/cost trade-offs.

**Deliverable:** Independently runnable and deployable RAG service with documented architecture, security controls, evaluation results and operating instructions.

**Mastery check:** Defend a design for a large, evolving technical corpus with strict latency, privacy and quality requirements.

---

## Dataset and evaluation principles

Dataset choice happens **before coding each project**. We prioritize real sources, established relevance/evidence annotations, reproducible versions and explicit development/test splits.

| Need | Candidate source | Important caveat |
|---|---|---|
| Small end-to-end baseline | Curated technical docs + manually reviewed questions | Keep small and inspectable; don't over-engineer generation |
| Ingestion/format quality | Real Markdown, HTML, DOCX and complex PDFs | Evaluate extraction independently of retrieval |
| Chunking and evidence boundaries | QASPER / structured long-document QA | Verify evidence annotation granularity and document access |
| Retrieval ranking | BEIR (e.g., SciFact, NFCorpus) | Document-level qrels don't automatically evaluate individual chunk IDs |
| Multi-hop query handling | HotpotQA | Preserve supporting-fact provenance and handle its task assumptions |
| Grounding and answer evaluation | RAGBench + application-specific reviewed examples | Validate metric definitions and label suitability |
| Production capstone | Versioned realistic technical-document collection | Maintain held-out regression tests and access-control cases |

**Evaluation rules:**
1. Freeze corpus, queries, labels, model versions and indexing configuration for each comparison.
2. Tune on development data; keep a held-out test split untouched until final reporting.
3. Report per-query failures, not just aggregate scores.
4. Separate **retrieval quality** from **answer quality**, and also measure latency and cost.
5. Treat generated relevance labels and LLM-judge ratings as provisional until validated.
6. Never assume a more complex method is better; document negative findings too.

## How we learn: design first, code second

Every project follows the same cycle:

1. **Problem and intuition** — What breaks in the simpler system? Work through a concrete example.
2. **Design exercise** — Propose data flow, interfaces, metadata, storage and expected failure cases.
3. **Incremental implementation** — Write the core logic yourself; use maintained libraries rather than duplicating commodity functionality.
4. **Inspect and debug** — Read real extracted text, chunks, rankings and answer evidence.
5. **Controlled evaluation** — Compare against the project baseline using appropriate metrics and unchanged data.
6. **Mastery checkpoint** — Explain the architecture, implement a key component independently and defend trade-offs.
7. **Document and commit** — Record decisions, example output, results, limitations and run instructions in that project's README.

**Two definitions of done:**
- **Engineering complete:** Reproducible run, reasonable tests/checks, evaluated results, README and Git commit.
- **Mastered:** Able to explain, rebuild the core pipeline, diagnose failures and make an architecture decision without copying the solution.

## Project independence and development standards

- Each project has its **own Git repository**, `pyproject.toml`, `uv.lock`, `.venv`, README and commands. The root `rag/` folder is just a local organizer.
- Use **Python and `uv`**, minimal files, explicit configuration and environment variables. Never commit secrets, large downloaded corpora, local indexes or virtual environments.
- Each project must run from a fresh clone, with documented dataset download/preparation commands; a shared local dataset cache is fine, but not an undocumented dependency.
- Prefer maintained LangChain/LangGraph/Chroma/DeepEval utilities when appropriate, but understand the abstractions and their failure modes.
- Re-implement foundational learning concepts when valuable; don't rewrite framework infrastructure for its own sake.
- Update the project README and commit after each verified milestone. A passing script alone does not equal mastery.

## Advanced topics kept outside the core critical path

- **Multimodal RAG:** A focused extension for images, tables, charts and page layout after mastering text/document pipelines.
- **GraphRAG:** An optional specialization for entity relationships and graph-guided/global retrieval.
- **RAPTOR and research-specific retrieval methods:** Focused experiments only when a concrete failure case justifies them.
- **Embedding model fine-tuning:** Study trade-offs; implement only when domain-specific evaluation warrants it.
- **Agentic RAG and multi-agent RAG:** Reserved for the separate Agentic AI track.
- **MCP:** Reserved for the subsequent MCP engineering track.

## Progress

| Project | Status |
|---|---|
| 00 — Minimal RAG | Not started |
| 01 — Document Engineering | Not started |
| 02 — Chunking Engineering | Not started |
| 03 — Retrieval Foundations | Not started |
| 04 — Advanced Retrieval | Not started |
| 05 — Query Intelligence | Not started |
| 06 — Grounded Generation | Not started |
| 07 — Production RAG | Not started |

**Next milestone:** Create `00-minimal-rag/` as the first standalone project. Build a simple complete pipeline, establish a reviewed baseline, and practice explaining each stage before moving on.
