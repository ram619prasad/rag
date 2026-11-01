
from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def run_markdown_chunking(file_path: str) -> None:
    text = Path(file_path).read_text(encoding="utf-8")

    headers_to_split_on = [
        ("#", "document_title"),
        ("##", "section"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=True,
    )

    sections = markdown_splitter.split_text(text)

    print("=== Markdown Sections ===")
    print("Total sections:", len(sections))

    for index, section in enumerate(sections, start=1):
        print(f"\nSECTION {index}")
        print("Metadata:", section.metadata)
        print("Content:", repr(section.page_content))

    token_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=40,
        chunk_overlap=0,
    )

    chunks = token_splitter.split_documents(sections)

    print("\n=== Final Structure-Aware Chunks ===")
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nCHUNK {index}")
        print("Metadata:", chunk.metadata)
        print("Content:", repr(chunk.page_content))


if __name__ == "__main__":
    run_markdown_chunking("data/chunking_benchmark.md")
