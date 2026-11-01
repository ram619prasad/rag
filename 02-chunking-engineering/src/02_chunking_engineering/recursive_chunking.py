
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def run_recursive_chunking(
    file_path: str,
    chunk_size: int = 300,
) -> list[Document]:

    text = Path(file_path).read_text(encoding="utf-8")

    document = Document(
        page_content=text,
        metadata={
            "source": file_path,
            "format": "markdown",
        },
    )

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=0,
        length_function=len,
        add_start_index=True,
    )

    chunks = splitter.split_documents([document])

    print("Original document:", len(text))
    print("Chunk size:", chunk_size)
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n{'=' * 55}")
        print(f"CHUNK {index}")
        print("Characters:", len(chunk.page_content))
        print("Start index:", chunk.metadata.get("start_index"))
        print("=" * 55)
        print(repr(chunk.page_content))

    return chunks


if __name__ == "__main__":
    run_recursive_chunking(
        "data/chunking_benchmark.md",
        chunk_size=300,
    )
