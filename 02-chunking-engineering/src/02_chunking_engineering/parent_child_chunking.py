
from pathlib import Path

from langchain_chroma import Chroma
from langchain_classic.retrievers.parent_document_retriever import (
    ParentDocumentRetriever,
)
from langchain_classic.storage import InMemoryStore
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter


FILE_PATH = Path("data/chunking_benchmark.md")


def main():
    text = FILE_PATH.read_text(encoding="utf-8")

    # document = Document(
    #     page_content=text,
    #     metadata={"source": str(FILE_PATH)},
    # )
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document_title"),
            ("##", "section"),
        ],
        strip_headers=True,
    )

    documents = header_splitter.split_text(text)

    for document in documents:
        document.metadata["source"] = str(FILE_PATH)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # # Large chunks returned as context.
    # parent_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=500,
    #     chunk_overlap=0,
    # )

    # Small chunks embedded for semantic search.
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=120,
        chunk_overlap=0,
    )

    vectorstore = Chroma(
        collection_name="parent_child_experiment",
        embedding_function=embeddings,
    )

    docstore = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        # parent_splitter=parent_splitter,
        child_splitter=child_splitter,
        search_kwargs={"k": 2},
    )

    retriever.add_documents(documents)

    query = (
        "What should engineers check before "
        "restarting a PostgreSQL replica?"
    )

    print("\n=== Query ===")
    print(query)

    # Inspect child matches directly.
    child_matches = vectorstore.similarity_search(
        query,
        k=2,
    )

    print("\n=== Matching Child Chunks ===")
    for index, child in enumerate(child_matches, 1):
        print(f"\nCHILD {index}")
        print("Parent ID:", child.metadata.get("doc_id"))
        print("Text:", child.page_content)

    # Retrieve larger parent chunks.
    parents = retriever.invoke(query)

    print("\n=== Retrieved Parent Chunks ===")
    for index, parent in enumerate(parents, 1):
        print(f"\nPARENT {index}")
        print("Characters:", len(parent.page_content))
        print("Source:", parent.metadata.get("source"))
        print("Text:", parent.page_content)


if __name__ == "__main__":
    main()
