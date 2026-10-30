# Project 00 — Minimal End-to-End RAG

A small, independently runnable Retrieval-Augmented Generation (RAG) application that answers questions using a Kubernetes Horizontal Pod Autoscaler (HPA) Markdown document.

The purpose is to understand the complete RAG workflow before introducing more advanced ingestion, chunking, retrieval, and evaluation techniques.

## 1. Problem and Objective

A language model can answer from its pretrained knowledge, but our application should answer **using supplied source evidence** and acknowledge when the source does not support an answer.

Our system must:

- Load a local Markdown document.
- Split the text into searchable chunks.
- Generate embeddings and store them in a vector database.
- Retrieve the top three relevant chunks.
- Generate an answer using retrieved context.
- Include supporting source identifiers.
- Abstain when the provided evidence is insufficient.
- Evaluate retrieval quality independently from answer generation.

## 2. System Architecture

### 2.1 Indexing Pipeline

Indexing prepares the documents for semantic retrieval.

```text
data/kubernetes_hpa.md
          |
          v
    Document Loader
          |
          v
  LangChain Document
          |
          v
 RecursiveCharacterTextSplitter
 chunk_size = 500
 chunk_overlap = 50
          |
          v
       16 Chunks
          |
          v
     OpenAI Embeddings
  text-embedding-3-small
          |
          v
     Chroma Vector DB
  Collection: minimal_rag
          |
          v
  Persistent Vector Index
```

Each indexed record contains:

```text
Chunk ID
    |
    +-- Original chunk text
    |
    +-- Embedding vector
    |
    +-- Source metadata
```

### 2.2 Retrieval and Generation Pipeline

```text
       User Question
             |
             v
       Query Embedding
             |
             v
     Chroma Vector Search
             |
             v
      Top 3 Relevant Chunks
             |
             v
    Context + Source IDs
             |
             v
      ChatPromptTemplate
             |
             v
         ChatOpenAI
        gpt-4.1-mini
             |
             v
       StrOutputParser
             |
             v
  Grounded Answer + Citations
```

The LLM is instructed to use only the retrieved evidence. If the context is insufficient, it should respond:

> I don't have enough information in the provided documents.

This instruction reduces unsupported generation but does not guarantee factual correctness or grounding.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Package management | uv |
| Document abstraction | LangChain Document |
| Text splitting | RecursiveCharacterTextSplitter |
| Embeddings | OpenAI text-embedding-3-small |
| Vector database | Chroma |
| Semantic retrieval | Chroma similarity search |
| LLM | GPT-4.1 mini |
| Prompt management | ChatPromptTemplate |
| Output parsing | StrOutputParser |
| Evaluation | Manual evaluation + Evidence Hit@3 |

We use maintained LangChain and Python libraries rather than implementing retrieval infrastructure from scratch.

LangGraph is intentionally not used because this baseline does not require conditional routing or stateful orchestration.

## 4. Dataset

### 4.1 Source Document

**File:** `data/kubernetes_hpa.md`

The document contains 5,620 characters covering:

- Horizontal Pod Autoscaler fundamentals
- CPU utilization and replica calculations
- Rolling updates
- Scaling stability and flapping
- Minimum and maximum replica limits
- Kubernetes HPA YAML configuration
- Troubleshooting

### 4.2 Chunking Configuration

```python
RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
```

**Result:** 16 chunks.

The splitter attempts to preserve paragraph, newline, and word boundaries before splitting at the character level.

Chunk lengths vary because the splitter does not force every chunk to contain exactly 500 characters.

### 4.3 Evaluation Dataset

**File:** `data/evaluation.json`

The evaluation dataset contains six manually specified questions:

| Category | Questions |
|---|---:|
| Answerable | 4 |
| Unanswerable | 2 |
| Total | 6 |

Evaluation questions are maintained separately from source documents and are not indexed into Chroma.

## 5. Implementation

### 5.1 Document Loading

The loader reads the Markdown file and creates a LangChain `Document`.

```python
Document(
    page_content=content,
    metadata={"source": source_path},
)
```

The `page_content` stores document text, while `metadata` enables traceability.

### 5.2 Text Chunking

The document is divided into 16 smaller sections using LangChain's recursive text splitter.

Each chunk preserves the original document's source metadata.

We also assign unique chunk identifiers:

```text
kubernetes_hpa_chunk:000
kubernetes_hpa_chunk:001
...
kubernetes_hpa_chunk:015
```

These identifiers distinguish individual chunks originating from the same source file.

### 5.3 Embeddings

We use:

```python
OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

The model produces 1,536-dimensional embeddings by default.

Embeddings represent text numerically, allowing semantic similarity searches.

### 5.4 Chroma Vector Store

```python
Chroma(
    collection_name="minimal_rag",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)
```

The collection stores chunk text, embeddings, identifiers, and metadata.

Persistence allows us to reuse indexed embeddings between application runs.

### 5.5 Retrieval

We use:

```python
vector_store.similarity_search(
    query=question,
    k=3,
)
```

For debugging, we can inspect distances using:

```python
vector_store.similarity_search_with_score(
    query=question,
    k=3,
)
```

Smaller returned distances indicate closer matches under the configured vector metric.

Distances are not probabilities of relevance or correctness.

### 5.6 Grounded Generation

The application formats retrieved chunks with source identifiers and passes them to the LLM.

LangChain Expression Language connects the components:

```python
chain = prompt | llm | StrOutputParser()
```

The chain produces an answer using the provided context.

## 6. Local Setup

From the `00-minimal-rag` project directory:

```bash
uv sync
```

Set your OpenAI API key in your local environment:

```bash
export OPENAI_API_KEY="your-api-key"
```

Do not commit API keys or local `.env` files.

### Run Individual Modules

```bash
# Document loading
uv run python -m minimal_rag.loader

# Text chunking
uv run python -m minimal_rag.chunker

# Embedding and Chroma indexing
uv run python -m minimal_rag.embedding

# Semantic retrieval
uv run python -m minimal_rag.retriever

# End-to-end RAG
uv run python -m minimal_rag.rag

# Evaluation
uv run python -m minimal_rag.evaluation
```

The commands assume the modules use the filenames above.

## 7. Retrieval Experiment

### Question

> Which controller manages ReplicaSets during rolling updates?

### Retrieved Results

| Rank | Chunk ID | Distance |
|---|---|---:|
| 1 | `kubernetes_hpa_chunk:005` | 0.7110 |
| 2 | `kubernetes_hpa_chunk:004` | 0.9521 |
| 3 | `kubernetes_hpa_chunk:006` | 0.9617 |

### Findings

**Rank 1:** Directly answers the question.

The passage explains that HPA controls the desired replica count on the Deployment, while the Deployment controller manages the underlying ReplicaSets.

**Rank 2:** Contains a replica calculation and the beginning of the rolling-update section.

This demonstrates how chunk boundaries can influence retrieval.

**Rank 3:** Provides additional supporting context about how Deployment and StatefulSet scaling differs.

### Generated Answer

The RAG system correctly identified the Deployment controller and cited supporting chunks `005` and `006`.

This verifies that our indexing, retrieval, context formatting, and generation pipeline work together for this question.

## 8. Evaluation Methodology

We evaluated three separate dimensions.

### 8.1 Evidence Hit@3

Measures whether at least one of the top three retrieved chunks matches manually identified supporting evidence.

```text
Evidence Hit@3 =
    Number of answerable questions with evidence found
    --------------------------------------------------
              Number of answerable questions
```

This metric measures evidence discovery, not whether all necessary evidence has been retrieved.

### 8.2 Answer Correctness

Measures whether generated answers match manually specified reference answers in meaning.

Exact string matching is not used because multiple phrasings may be correct.

### 8.3 Abstention

Measures whether the system acknowledges insufficient evidence for questions that cannot be answered from the indexed document.

### 8.4 Groundedness and Citations

We qualitatively inspected whether answers were supported by retrieved passages.

However, independent claim-level citation verification has not yet been implemented.

## 9. Evaluation Results

### 9.1 Question-Level Results

| ID | Question topic | Result |
|---|---|---|
| q001 | ReplicaSet controller | Correct |
| q002 | Replica calculation | Correct |
| q003 | Scaling stabilization | Correct |
| q004 | Minimum and maximum replicas | Correct |
| q005 | Kubernetes creator and year | Correctly abstained |
| q006 | orders-api database | Correctly abstained |

### 9.2 Aggregate Results

| Metric | Result |
|---|---:|
| Evidence Hit@3 | **4/4 (100%)** |
| Answer correctness | **4/4 (100%)** |
| Correct abstention | **2/2 (100%)** |
| Independent citation verification | Not measured |

The Evidence Hit@3 result uses provisional chunk-level relevance annotations and should not be interpreted as independently audited retrieval performance.

### 9.3 Interpretation

All six questions exhibited the expected behavior.

However, these results do not establish general performance because:

- The corpus contains only one document.
- The evaluation set has six questions.
- The questions are relatively straightforward.
- Several questions closely match the document wording.
- Chunk-level relevance labels have not been independently audited.
- Citations are generated by the LLM and are not programmatically verified.

This evaluation is intended to validate the initial architecture rather than establish production-level retrieval quality.

## 10. Important Learnings

### Document Engineering

- LangChain `Document` separates source text from metadata.
- Source metadata enables traceability.
- Multiple chunks can share the same source but require distinct identifiers.

### Chunking

- Smaller chunks provide focused retrieval units.
- Recursive splitting attempts to respect text boundaries.
- Fixed-size splitting can fragment formulas, explanations, or YAML configurations.
- Chunk overlap may preserve some information across boundaries but increases redundancy.

### Embeddings and Retrieval

- Embeddings convert text into numerical vectors.
- Semantic retrieval can match related meanings even when query wording differs.
- Chroma persists embeddings, original text, and metadata.
- Vector proximity is not equivalent to answer correctness.
- Metadata filtering can restrict the eligible retrieval set.

### Grounded Generation

- Retrieved evidence must be formatted clearly for the LLM.
- Source IDs help trace answers to retrieved chunks.
- Prompt instructions can encourage abstention when evidence is insufficient.
- LLM-generated citations require independent verification for stronger reliability guarantees.

### Evaluation

- Retrieval correctness and generation correctness are different problems.
- A correct answer may still lack supporting evidence.
- Evidence Hit@K does not measure complete evidence coverage.
- Small evaluation datasets help debug a pipeline but cannot establish generalization.

## 11. Limitations

Our minimal RAG system currently has several limitations:

1. Supports a single educational Markdown document.
2. Uses one fixed chunking configuration.
3. Uses only semantic similarity retrieval.
4. Does not implement hybrid search or reranking.
5. Does not automatically detect document updates or deletions.
6. Does not validate generated citations programmatically.
7. Does not measure latency or token costs systematically.
8. Has limited evaluation coverage.
9. Does not include authentication, access control, or a production API.

These limitations are intentional. Later projects will address them through focused experiments.

## 12. Project Outcome

### Engineering Outcome

Implemented an end-to-end RAG application using:

- Python
- LangChain
- OpenAI embeddings
- Chroma
- ChatOpenAI

The application can load documents, create embeddings, retrieve relevant passages, generate source-referenced answers, and abstain when evidence is insufficient.

### Learning Outcome

Gained practical understanding of the indexing and querying pipelines and how document loading, chunking, embeddings, vector search, context construction, generation, and evaluation fit together.

The next goal is to improve the individual components systematically rather than add complexity without evidence.

---

