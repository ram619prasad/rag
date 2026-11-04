from pathlib import Path
from rank_bm25 import BM25Okapi
import numpy as np
import json
import re
import csv
import ir_measures
from ir_measures import R, P, RR, nDCG

DATA_DIR = Path(__file__).resolve().parent / "data" / "scifact"

def tokenize(text: str) -> list[str]:
    # Simple, consistent word-level tokenization.
    return re.findall(r"\b\w+\b", text.lower())


def load_jsonl(path: Path) -> dict:
    records = {}

    with path.open('r', encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            
            record = json.loads(line)
            record_id = record.pop("_id")
            records[record_id] = record

    return records

def load_qrels(path: Path) -> dict:
    qrels = {}

    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            query_id = row["query-id"]
            document_id = row["corpus-id"]
            relevance = int(row["score"])

            qrels.setdefault(query_id, {})[document_id] = relevance

    return qrels


def verify_retrieval(
    query_id: str,
    top_indices,
    document_ids: list[str],
    scores,
    qrels: dict,
) -> None:

    if query_id not in qrels:
        print(f"No ground truth for query {query_id}")
        return

    # Ground truth for just this query
    query_qrels = {
        query_id: qrels[query_id]
    }
    
    print(query_qrels)

    # Convert BM25 results into ir-measures format
    query_run = {
        query_id: {
            document_ids[int(index)]: float(scores[index])
            for index in top_indices
        }
    }

    k = len(top_indices)

    metrics = [
        R@k,
        P@k,
        RR@k,
        nDCG@k,
    ]

    results = ir_measures.calc_aggregate(
        metrics,
        query_qrels,
        query_run,
    )

    print(f"\n=== Evaluation: Query {query_id} ===")

    for rank, index in enumerate(top_indices, start=1):
        doc_id = document_ids[int(index)]
        relevant = qrels[query_id].get(doc_id, 0) > 0

        print(
            f"Rank {rank} | "
            f"Doc: {doc_id} | "
            f"Relevant: {relevant}"
        )

    print("\n=== Retrieval Metrics ===")

    for metric in metrics:
        print(f"{metric}: {results[metric]:.3f}")



def main():
    # 1. Load SciFact data.
    corpus = load_jsonl(DATA_DIR / "corpus.jsonl")
    queries = load_jsonl(DATA_DIR / "queries.jsonl")

    # 2. Preserve document IDs in index order.
    document_ids = list(corpus.keys())

    # 3. Combine title and abstract.
    texts = [
        f"{corpus[doc_id].get('title', '')} "
        f"{corpus[doc_id].get('text', '')}"
        for doc_id in document_ids
    ]

    # 4. Tokenize each document.
    tokenized_corpus = [
        tokenize(text)
        for text in texts
    ]

    # 5. Build BM25 index.
    bm25 = BM25Okapi(tokenized_corpus)

    # 6. Choose a real SciFact query.
    query_id = "1303"
    query = queries[query_id]["text"]

    print(f"Query ID: {query_id}")
    print(f"Query: {query}")

    # 7. Score all documents.
    scores = bm25.get_scores(tokenize(query))

    # 8. Find top 5 indices in descending score order.
    top_indices = np.argsort(-scores)[:5]

    print("\n=== Top 5 BM25 Results ===")

    for rank, index in enumerate(top_indices, start=1):
        doc_id = document_ids[index]
        document = corpus[doc_id]

        print(f"\nRank: {rank}")
        print(f"Document ID: {doc_id}")
        print(f"BM25 Score: {scores[index]:.3f}")
        print(f"Title: {document.get('title', '')}")
        print(
            f"Abstract: "
            f"{document.get('text', '')[:300]}..."
        )
        
    test_qrels = load_qrels(
        DATA_DIR / "qrels" / "test.tsv"
    )

    verify_retrieval(
        query_id=query_id,
        top_indices=top_indices,
        document_ids=document_ids,
        scores=scores,
        qrels=test_qrels,
    )


if __name__ == "__main__":
    main()
    
