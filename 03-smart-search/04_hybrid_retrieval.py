
import re
from pathlib import Path
import csv
import json
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()
DATA_DIR = Path(__file__).resolve().parent / "data" / "scifact"
DB_DIR = Path(__file__).resolve().parent / "chroma_db"

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


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def create_hybrid_retriever(corpus: dict, vector_store: Chroma):
    # Convert SciFact records to LangChain Documents.
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

    # BM25 keyword retriever.
    bm25 = BM25Retriever.from_documents(
        documents,
        preprocess_func=tokenize,
    )
    bm25.k = 20

    # Existing Chroma semantic retriever.
    semantic = vector_store.as_retriever(
        search_kwargs={"k": 20}
    )

    # Hybrid retrieval using weighted RRF.
    hybrid = EnsembleRetriever(
        retrievers=[bm25, semantic],
        weights=[0.5, 0.5],
        id_key="doc_id",
    )

    return hybrid



import ir_measures
from ir_measures import R, P, RR, nDCG


def verify_hybrid(
    query_id: str,
    results: list,
    qrels: dict,
):
    if query_id not in qrels:
        print(f"No qrels for query {query_id}")
        return

    k = len(results)

    # Ground-truth relevance labels.
    query_qrels = {
        query_id: qrels[query_id]
    }

    # Convert ranked LangChain Documents into
    # an ir-measures run.
    query_run = {
        query_id: {
            doc.metadata["doc_id"]: k - rank
            for rank, doc in enumerate(results)
        }
    }

    metrics = [
        R@k,
        P@k,
        RR@k,
        nDCG@k,
    ]

    scores = ir_measures.calc_aggregate(
        metrics,
        query_qrels,
        query_run,
    )

    print("\n=== Hybrid Retrieval Evaluation ===")

    for rank, doc in enumerate(results, start=1):
        doc_id = doc.metadata["doc_id"]
        relevant = qrels[query_id].get(doc_id, 0) > 0

        print(
            f"Rank {rank} | "
            f"Doc ID: {doc_id} | "
            f"Relevant: {relevant}"
        )

    for metric in metrics:
        print(f"{metric}: {scores[metric]:.3f}")


def main():
    corpus = load_jsonl(DATA_DIR / "corpus.jsonl")
    queries = load_jsonl(DATA_DIR / "queries.jsonl")
    test_qrels = load_qrels(DATA_DIR / "qrels/test.tsv")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = Chroma(
        collection_name="semantic_demo",
        embedding_function=embeddings,
        persist_directory=str(DB_DIR),
    )

    hybrid = create_hybrid_retriever(
        corpus=corpus,
        vector_store=vector_store,
    )

    query_id = "1"
    query = queries[query_id]["text"]

    results = hybrid.invoke(query)[:5]

    for rank, doc in enumerate(results, start=1):
        print(
            f"Rank {rank} | "
            f"Doc ID: {doc.metadata['doc_id']} | "
            f"{doc.metadata['title']}"
        )
        
    verify_hybrid(
        query_id=query_id,
        results=results,
        qrels=test_qrels,
    )
        
        
if __name__ == "__main__":
    main()