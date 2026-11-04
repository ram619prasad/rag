
import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data" / "scifact"


def load_jsonl(path: Path) -> dict:
    records = {}

    with path.open("r", encoding="utf-8") as file:
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


def main():
    corpus = load_jsonl(DATA_DIR / "corpus.jsonl")
    queries = load_jsonl(DATA_DIR / "queries.jsonl")

    train_qrels = load_qrels(DATA_DIR / "qrels" / "train.tsv")
    test_qrels = load_qrels(DATA_DIR / "qrels" / "test.tsv")

    print("=== SciFact Dataset ===")
    print(f"Documents: {len(corpus)}")
    print(f"Queries: {len(queries)}")
    print(f"Train queries with labels: {len(train_qrels)}")
    print(f"Test queries with labels: {len(test_qrels)}")

    # Verify references in both ground-truth splits.
    for split_name, qrels in [
        ("train", train_qrels),
        ("test", test_qrels),
    ]:
        for query_id, relevant_docs in qrels.items():
            assert query_id in queries, (
                f"Unknown query in {split_name}: {query_id}"
            )

            for doc_id in relevant_docs:
                assert doc_id in corpus, (
                    f"Unknown document in {split_name}: {doc_id}"
                )

    print("\nGround-truth references verified.")

    # Inspect one query and its first relevant document.
    query_id = next(iter(test_qrels))
    relevant_doc_id = next(iter(test_qrels[query_id]))

    query = queries[query_id]
    document = corpus[relevant_doc_id]

    print("\n=== Example Query ===")
    print(f"Query ID: {query_id}")
    print(f"Query: {query['text']}")

    print("\n=== Relevant Document ===")
    print(f"Document ID: {relevant_doc_id}")
    print(f"Title: {document['title']}")
    print(f"Abstract: {document['text'][:500]}...")

    print(
        f"\nRelevance score: "
        f"{test_qrels[query_id][relevant_doc_id]}"
    )


if __name__ == "__main__":
    main()
