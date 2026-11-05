
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"


def main():
    vector_store = Chroma(
        collection_name="semantic_demo",
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-small",
        ),
        persist_directory=str(DB_DIR),
    )

    query = "How does muscle activation affect movement?"

    # First search without any filtering.
    print("\n=== Unfiltered Search ===")

    results = vector_store.similarity_search_with_score(
        query=query,
        k=5,
    )

    for rank, (doc, distance) in enumerate(results, 1):
        print(
            f"{rank}. {doc.metadata['doc_id']} | "
            f"{distance:.4f} | "
            f"{doc.metadata['title']}"
        )

    # Restrict retrieval to selected SciFact documents.
    allowed_ids = [
        "12631697",
        "43566999",
        "8771704",
    ]

    print("\n=== Metadata-Filtered Search ===")
    metadata_filter = {
        "doc_id": {"$in": allowed_ids}
    }

    filtered_results = vector_store.similarity_search_with_score(
        query=query,
        k=5,
        filter=cast(dict[str, str], metadata_filter),
    )

    for rank, (doc, distance) in enumerate(
        filtered_results, 1
    ):
        print(
            f"{rank}. {doc.metadata['doc_id']} | "
            f"{distance:.4f} | "
            f"{doc.metadata['title']}"
        )


if __name__ == "__main__":
    main()
