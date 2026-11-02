
from pathlib import Path
from time import perf_counter
import tiktoken


from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


FILE_PATH = "data/semantic_benchmark.md"

encoding = tiktoken.get_encoding("cl100k_base")


def print_chunks(name: str, chunks: list[str]) -> None:
    print(f"\n=== {name} ===")
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nCHUNK {index}")
        print("Characters:", len(chunk))
        print("Start:", repr(chunk[:120]))
        print("End:", repr(chunk[-120:]))


def run_experiment() -> None:
    text = Path(FILE_PATH).read_text(encoding="utf-8")

    print("Document characters:", len(text))

    # Baseline: no embedding model required.
    recursive = RecursiveCharacterTextSplitter(
        chunk_size=650,
        chunk_overlap=0,
    )

    baseline_chunks = recursive.split_text(text)
    print_chunks("Recursive Chunking", baseline_chunks)

    # Local embedding model.
    print("\nLoading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    # Semantic boundaries based on embedding distances.
    semantic = SemanticChunker(
        embeddings=embeddings,
        buffer_size=1,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=80,
    )

    start = perf_counter()
    semantic_chunks = [
        chunk.strip()
        for chunk in semantic.split_text(text)
        if chunk.strip()
    ]
    for index, chunk in enumerate(semantic_chunks, start=1):
        print(
            f"Chunk {index}: "
            f"{len(chunk)} characters, "
            f"{len(encoding.encode(chunk))} tokens"
        )
    elapsed = perf_counter() - start

    print_chunks("Semantic Chunking", semantic_chunks)
    print(f"\nSemantic split time: {elapsed:.3f} seconds")


if __name__ == "__main__":
    run_experiment()
