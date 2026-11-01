
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter


def run_fixed_size_chunking(
    file_path: str,
    chunk_size: int = 150,
) -> list[Document]:

    text = Path(file_path).read_text(encoding="utf-8")

    document = Document(
        page_content=text,
        metadata={
            "source": file_path,
            "format": "markdown",
        },
    )

    splitter = CharacterTextSplitter(
        separator="",
        chunk_size=chunk_size,
        chunk_overlap=0,
        length_function=len,
        strip_whitespace=False,
        add_start_index=True,
    )

    chunks = splitter.split_documents([document])

    print(f"Original document: {len(text)} characters")
    print(f"Chunk size: {chunk_size}")
    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n{'=' * 55}")
        print(f"CHUNK {index}")
        print(f"Characters: {len(chunk.page_content)}")
        print(f"Start index: {chunk.metadata.get('start_index')}")
        print(f"{'=' * 55}")
        print(repr(chunk.page_content))

    return chunks


if __name__ == "__main__":
    run_fixed_size_chunking(
        "data/chunking_benchmark.md",
        chunk_size=300,
    )
