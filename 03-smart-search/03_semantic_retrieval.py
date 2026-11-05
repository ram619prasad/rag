from pathlib import Path
from dotenv import load_dotenv
import json
import csv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import ir_measures
from ir_measures import R, P, RR, nDCG

load_dotenv()
DB_DIR = Path(__file__).resolve().parent / "chroma_db"
DATA_DIR = Path(__file__).resolve().parent / "data" / "scifact"

def load_jsonl(path: Path) -> dict:
    results = {}
    
    with path.open('r', encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            
            record = json.loads(line)
            record_id = record.pop("_id")
            results[record_id] = record     
    
    return results

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

def index_corpus(corpus: dict, vector_store):
    batch_size = 100
    existing_ids = set(
        vector_store.get(include=[])["ids"]
    )
    pending_ids = [
        doc_id
        for doc_id in corpus
        if doc_id not in existing_ids
    ]
    
    print(f"Already indexed: {len(existing_ids)}")
    print(f"Documents remaining: {len(pending_ids)}")  
    
    for start in range(0, len(pending_ids), batch_size):
        batch_ids = pending_ids[start:start+batch_size]
        
        documents = [
            Document(
                id=doc_id,
                page_content=(
                    f"{corpus[doc_id].get('title', '')} "
                    f"{corpus[doc_id].get('text', '')}"
                ),
                metadata={
                    "doc_id": doc_id,
                    "title": corpus[doc_id].get("title", ""),
                },
            )
            for doc_id in batch_ids
        ]
        
        vector_store.add_documents(
            documents,
            ids=batch_ids
        )
        
        print(
            f"Indexed {start + len(batch_ids)}"
            f"/{len(pending_ids)} remaining documents"
        )

    print(f"Total indexed: {vector_store._collection.count()}")



def search_semantic(vector_store, query, k = 5):
    results = vector_store.similarity_search_with_score(
        query=query,
        k=k,
    )

    return [
        {
            "doc_id": doc.metadata["doc_id"],
            "distance": float(distance),
            "title": doc.metadata["title"],
        }
        for doc, distance in results
    ]

def verify_semantic(
    query_id: str,
    results: list[dict],
    qrels: dict,
):
    if query_id not in qrels:
        print(f"No ground truth for query {query_id}")
        return

    k = len(results)

    query_qrels = {
        query_id: qrels[query_id]
    }
    
    query_run = {
        query_id: {
            result["doc_id"]: k - rank
            for rank, result in enumerate(results)
        }
    }
    
    metrics = [R@k, P@k, RR@k, nDCG@k]

    scores = ir_measures.calc_aggregate(
        metrics,
        query_qrels,
        query_run,
    )

    print("\n=== Retrieval Verification ===")

    for rank, result in enumerate(results, start=1):
        doc_id = result["doc_id"]
        relevant = qrels[query_id].get(doc_id, 0) > 0

        print(
            f"Rank {rank} | "
            f"Doc: {doc_id} | "
            f"Distance: {result['distance']:.4f} | "
            f"Relevant: {relevant}"
        )

    print("\n=== Retrieval Metrics ===")

    for metric in metrics:
        print(f"{metric}: {scores[metric]:.3f}")



def main():
    queries = load_jsonl(
        DATA_DIR / "queries.jsonl"
    )

    test_qrels = load_qrels(
        DATA_DIR / "qrels" / "test.tsv"
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
    )

    # Reopen the existing verified collection.
    vector_store = Chroma(
        collection_name="semantic_demo",
        embedding_function=embeddings,
        persist_directory=str(DB_DIR),
    )

    for query_id in ["1", "1303"]:
        if query_id not in test_qrels:
            print(f"\nSkipping {query_id}: no test qrels")
            continue

        query = queries[query_id]["text"]

        print(f"\nQuery ID: {query_id}")
        print(f"Query: {query}")

        results = search_semantic(
            vector_store,
            query,
            k=5,
            )

        verify_semantic(
            query_id=query_id,
            results=results,
            qrels=test_qrels,
        )


if __name__ == "__main__":
    main()




if __name__ == "__main__":
    main()