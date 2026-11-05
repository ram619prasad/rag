
import csv
import json
import random
import re
from pathlib import Path

import ir_measures
from ir_measures import R, P, RR, nDCG

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "scifact"
DB_DIR = BASE_DIR / "chroma_db"

SPLIT = "train"
QUERY_LIMIT = 20
TOP_K = 10
CANDIDATE_K = 20


def load_jsonl(path: Path) -> dict:
    records = {}

    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            record_id = record.pop("_id")
            records[record_id] = record

    return records


def load_qrels(path: Path) -> dict:
    qrels = {}

    with path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            query_id = row["query-id"]
            doc_id = row["corpus-id"]
            score = int(row["score"])

            qrels.setdefault(query_id, {})[doc_id] = score

    return qrels


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def create_retrievers(corpus: dict):
    documents = [
        Document(
            id=doc_id,
            page_content=(
                f"{record.get('title', '')} "
                f"{record.get('text', '')}"
            ),
            metadata={
                "doc_id": doc_id,
                "title": record.get("title", ""),
            },
        )
        for doc_id, record in corpus.items()
    ]

    bm25 = BM25Retriever.from_documents(
        documents,
        preprocess_func=tokenize,
    )
    bm25.k = CANDIDATE_K

    vector_store = Chroma(
        collection_name="semantic_demo",
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-small"
        ),
        persist_directory=str(DB_DIR),
    )

    # Ensure we're using our verified collection.
    assert len(vector_store.get(include=[])["ids"]) == len(corpus)

    semantic = vector_store.as_retriever(
        search_kwargs={"k": CANDIDATE_K}
    )

    hybrid = EnsembleRetriever(
        retrievers=[bm25, semantic],
        weights=[0.5, 0.5],
        c=60,
        id_key="doc_id",
    )

    return {
        "BM25": bm25,
        "Semantic": semantic,
        "Hybrid": hybrid,
    }


def to_run(documents: list[Document]) -> dict[str, float]:
    top_docs = documents[:TOP_K]

    document_ids: list[str] = [
        str(doc.metadata["doc_id"])
        for doc in top_docs
    ]

    if len(document_ids) != len(set(document_ids)):
        raise ValueError("Duplicate document IDs in retrieval results")

    return {
        doc_id: float(TOP_K - rank)
        for rank, doc_id in enumerate(document_ids)
    }



def analyze_failures(runs: dict, qrels: dict):
    print("\n=== Query-Level Analysis ===")

    for query_id in runs["BM25"]:
        scores = {}

        for name, run in runs.items():
            result = ir_measures.calc_aggregate(
                [R@5],
                {query_id: qrels[query_id]},
                {query_id: run[query_id]},
            )

            scores[name] = result[R@5]

        bm25 = scores["BM25"]
        semantic = scores["Semantic"]
        hybrid = scores["Hybrid"]

        if hybrid < semantic:
            category = "Hybrid worse than Semantic"
        elif hybrid > max(bm25, semantic):
            category = "Hybrid beats both"
        elif bm25 > semantic:
            category = "BM25 beats Semantic"
        elif semantic > bm25:
            category = "Semantic beats BM25"
        else:
            continue

        print(
            f"Query {query_id} | {category} | "
            f"BM25={bm25:.2f}, "
            f"Semantic={semantic:.2f}, "
            f"Hybrid={hybrid:.2f}"
        )


def main():
    corpus = load_jsonl(DATA_DIR / "corpus.jsonl")
    queries = load_jsonl(DATA_DIR / "queries.jsonl")

    qrels = load_qrels(
        DATA_DIR / "qrels" / f"{SPLIT}.tsv"
    )

    # Deterministic sample from labeled queries.
    query_ids = sorted(qrels)

    if QUERY_LIMIT is not None:
        query_ids = random.Random(42).sample(
            query_ids,
            min(QUERY_LIMIT, len(query_ids)),
        )

    selected_qrels = {
        query_id: qrels[query_id]
        for query_id in query_ids
    }

    retrievers = create_retrievers(corpus)

    runs = {
        name: {}
        for name in retrievers
    }

    for index, query_id in enumerate(query_ids, start=1):
        query = queries[query_id]["text"]

        print(
            f"Evaluating {index}/{len(query_ids)} "
            f"| Query {query_id}"
        )

        for name, retriever in retrievers.items():
            documents = retriever.invoke(query)

            runs[name][query_id] = to_run(documents)

    metrics = [
        R@5,
        R@10,
        P@10,
        RR@10,
        nDCG@10,
    ]

    evaluator = ir_measures.evaluator(
        metrics,
        selected_qrels,
    )

    print("\n=== Retrieval Benchmark ===")
    print(f"Split: {SPLIT}")
    print(f"Queries evaluated: {len(query_ids)}")

    for name, run in runs.items():
        scores = evaluator.calc_aggregate(run)

        print(f"\n{name}")

        for metric in metrics:
            print(f"{metric}: {scores[metric]:.4f}")
            
    analyze_failures(runs, selected_qrels)


if __name__ == "__main__":
    main()

