
from pathlib import Path

import tiktoken
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


FILE_PATH = Path("data/chunking_benchmark.md")
TOKEN_LIMIT = 80


def compare_retrieval(
    basic_chunks: list[Document],
    enriched_chunks: list[Document],
) -> None:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Separate indexes, identical embedding model.
    basic_store = Chroma.from_documents(
        documents=basic_chunks,
        embedding=embeddings,
        collection_name="basic_context_experiment",
    )

    enriched_store = Chroma.from_documents(
        documents=enriched_chunks,
        embedding=embeddings,
        collection_name="enriched_context_experiment",
    )

    queries = [
        "What should engineers check before restarting a database replica?",
        "How does Kubernetes scale application pods?",
        "What should engineers investigate during a payment incident?",
        "How does the API gateway protect services from excessive traffic?",
    ]

    for query in queries:
        print(f"\n{'=' * 70}")
        print("QUERY:", query)

        for label, store in [
            ("BASIC", basic_store),
            ("ENRICHED", enriched_store),
        ]:
            results = store.similarity_search(
                query,
                k=3,
            )

            print(f"\n--- {label} TOP 3 ---")

            for rank, doc in enumerate(results, start=1):
                print(
                    f"{rank}. "
                    f"Section: {doc.metadata.get('section')}"
                )

                # Remove contextual prefix for comparison.
                content = doc.page_content.split(
                    "\n\n",
                    maxsplit=1,
                )[-1]

                print("   Text:", content[:120])



def main():
    text = FILE_PATH.read_text(encoding="utf-8")
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # 1. Split by Markdown section.
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document_title"),
            ("##", "section"),
        ],
        strip_headers=True,
    )

    sections = header_splitter.split_text(text)

    # 2. Split each section into smaller chunks.
    # Use a character budget for this first comparison.
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=0,
    )

    basic_chunks: list[Document] = []
    enriched_chunks: list[Document] = []

    for section in sections:
        children = child_splitter.split_text(
            section.page_content
        )

        for child in children:
            metadata = {
                **section.metadata,
                "source": str(FILE_PATH),
            }

            # Baseline: content with metadata only.
            basic_chunks.append(
                Document(
                    page_content=child,
                    metadata=metadata,
                )
            )

            # Contextual: include the section and title
            # in the text that will be embedded.
            title = metadata.get(
                "document_title",
                "Unknown Document",
            )
            heading = metadata.get(
                "section",
                "General",
            )

            contextual_text = (
                f"Document: {title}\n"
                f"Section: {heading}\n\n"
                f"{child}"
            )

            enriched_chunks.append(
                Document(
                    page_content=contextual_text,
                    metadata=metadata,
                )
            )

    # 3. Compare token usage and inspect chunks.
    basic_tokens = sum(
        len(tokenizer.encode(doc.page_content))
        for doc in basic_chunks
    )

    enriched_tokens = sum(
        len(tokenizer.encode(doc.page_content))
        for doc in enriched_chunks
    )

    print("=== Contextual Enrichment ===")
    print("Basic chunks:", len(basic_chunks))
    print("Enriched chunks:", len(enriched_chunks))
    print("Basic tokens:", basic_tokens)
    print("Enriched tokens:", enriched_tokens)
    print("Additional tokens:", enriched_tokens - basic_tokens)

    print("\n=== Chunk Comparison ===")

    for index, (basic, enriched) in enumerate(
        zip(basic_chunks, enriched_chunks),
        start=1,
    ):
        print(f"\nCHUNK {index}")

        print("Metadata:", basic.metadata)

        print("\nBASIC:")
        print(basic.page_content[:160])

        print("\nENRICHED:")
        print(enriched.page_content[:240])

        print(
            "Tokens:",
            len(tokenizer.encode(basic.page_content)),
            "->",
            len(tokenizer.encode(enriched.page_content)),
        )

    oversized = [
        doc
        for doc in enriched_chunks
        if len(tokenizer.encode(doc.page_content)) > TOKEN_LIMIT
    ]

    print(
        f"\nEnriched chunks exceeding {TOKEN_LIMIT} tokens:",
        len(oversized),
    )
    
    compare_retrieval(
        basic_chunks=basic_chunks,
        enriched_chunks=enriched_chunks,
    )


if __name__ == "__main__":
    main()
