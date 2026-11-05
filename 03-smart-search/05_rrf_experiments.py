
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Reuse these functions from Module 04.
# Because the filename begins with a number, use
# importlib to load the existing script.
from importlib.util import (
    spec_from_file_location,
    module_from_spec,
)

BASE_DIR = Path(__file__).resolve().parent


spec = spec_from_file_location(
    "hybrid_module",
    BASE_DIR / "04_hybrid_retrieval.py",
)

if spec is None or spec.loader is None:
    raise ImportError("Cannot load 04_hybrid_retrieval.py")

module = module_from_spec(spec)
spec.loader.exec_module(module)

load_jsonl = module.load_jsonl
create_hybrid_retriever = module.create_hybrid_retriever

load_dotenv()

corpus = load_jsonl(BASE_DIR / "data/scifact/corpus.jsonl")
queries = load_jsonl(BASE_DIR / "data/scifact/queries.jsonl")

vector_store = Chroma(
    collection_name="semantic_demo",
    embedding_function=OpenAIEmbeddings(
        model="text-embedding-3-small"
    ),
    persist_directory=str(BASE_DIR / "chroma_db"),
)

query_id = "1"
query = queries[query_id]["text"]
target_id = "31715818"

for candidate_k in [20, 50]:
    for weight in [0.25, 0.50, 0.75]:
        hybrid = create_hybrid_retriever(
            corpus=corpus,
            vector_store=vector_store,
            bm25_weight=weight,
            candidate_k=candidate_k,
        )

        results = hybrid.invoke(query)

        ranked_ids = [
            doc.metadata["doc_id"]
            for doc in results
        ]

        target_rank = (
            ranked_ids.index(target_id) + 1
            if target_id in ranked_ids
            else None
        )

        print(
            f"Candidates: {candidate_k} | "
            f"BM25 weight: {weight:.2f} | "
            f"Target rank: {target_rank or 'Not found'} | "
            f"Top 5: {ranked_ids[:5]}"
        )
