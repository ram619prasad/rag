
from pathlib import Path

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


FILE_PATH = "data/chunking_benchmark.md"
ENCODING = "cl100k_base"


def compare_chunking() -> None:
    text = Path(FILE_PATH).read_text(encoding="utf-8")
    tokenizer = tiktoken.get_encoding(ENCODING)

    character_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=0,
    )

    token_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name=ENCODING,
        chunk_size=80,
        chunk_overlap=0,
    )

    experiments = {
        "Character-based (300 characters)": character_splitter,
        "Token-aware (80 tokens)": token_splitter,
    }

    for name, splitter in experiments.items():
        chunks = splitter.split_text(text)

        print(f"\n=== {name} ===")
        print("Total chunks:", len(chunks))

        for index, chunk in enumerate(chunks, start=1):
            token_count = len(tokenizer.encode(chunk))

            print(
                f"Chunk {index}: "
                f"{len(chunk)} chars, "
                f"{token_count} tokens"
            )

        print("\nFirst two chunks:")
        for chunk in chunks[:2]:
            print(repr(chunk))
            print("---")



def compare_lengths() -> None:
    text = Path(FILE_PATH).read_text(encoding="utf-8")
    tokenizer = tiktoken.get_encoding(ENCODING)

    print("=== Whole Document ===")
    print("Characters:", len(text))
    print("Tokens:", len(tokenizer.encode(text)))

    print("\n=== Same text length, different content ===")

    samples = [
        "PostgreSQL replication improves availability.",
        "SELECT * FROM payments WHERE status = 'FAILED';",
        "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥",
    ]

    for sample in samples:
        print(f"\nText: {sample}")
        print("Characters:", len(sample))
        print("Tokens:", len(tokenizer.encode(sample)))


if __name__ == "__main__":
    compare_chunking()
