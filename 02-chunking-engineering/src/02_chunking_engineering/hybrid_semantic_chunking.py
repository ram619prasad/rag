
from pathlib import Path

import tiktoken
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

FILE_PATH = "data/structured_semantic_benchmark.md"


def run_structure_token_baseline():
    text = Path(FILE_PATH).read_text(encoding="utf-8")
    tokenizer = tiktoken.get_encoding("cl100k_base")

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document_title"),
            ("##", "section"),
        ],
        strip_headers=True,
    )

    sections = markdown_splitter.split_text(text)

    token_splitter = (
        RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=80,
            chunk_overlap=0,
        )
    )

    chunks = token_splitter.split_documents(sections)

    print("\n=== Structure + Token Baseline ===")
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nCHUNK {index}")
        print("Section:", chunk.metadata.get("section"))
        print(
            "Tokens:",
            len(tokenizer.encode(chunk.page_content)),
        )
        print("Start:", repr(chunk.page_content[:100]))
        print("End:", repr(chunk.page_content[-100:]))

    return chunks



def run_hybrid_chunking():
    text = Path(FILE_PATH).read_text(encoding="utf-8")
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # Stage 1: Preserve document structure.
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document_title"),
            ("##", "section"),
        ],
        strip_headers=True,
    )

    sections = markdown_splitter.split_text(text)

    # Stage 2: Detect meaning changes within sections.
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    semantic_splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=80,
    )

    # Stage 3: Enforce token budget.
    token_splitter = (
        RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=80,
            chunk_overlap=0,
        )
    )

    final_chunks = []

    for section in sections:
        semantic_parts = semantic_splitter.split_text(
            section.page_content
        )

        for part in semantic_parts:
            if not part.strip():
                continue

            semantic_doc = Document(
                page_content=part.strip(),
                metadata=section.metadata.copy(),
            )

            final_chunks.extend(
                token_splitter.split_documents([semantic_doc])
            )

    print("Original sections:", len(sections))
    print("Final chunks:", len(final_chunks))

    for index, chunk in enumerate(final_chunks, start=1):
        tokens = len(tokenizer.encode(chunk.page_content))

        print(f"\n=== Chunk {index} ===")
        print("Section:", chunk.metadata.get("section"))
        print("Tokens:", tokens)
        print("Start:", repr(chunk.page_content[:100]))
        print("End:", repr(chunk.page_content[-100:]))

    assert all(
        len(tokenizer.encode(c.page_content)) <= 80
        for c in final_chunks
    )

    return final_chunks


if __name__ == "__main__":
    run_hybrid_chunking()
    run_structure_token_baseline()
