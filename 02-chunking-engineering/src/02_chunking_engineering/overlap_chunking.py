
from pathlib import Path

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


FILE_PATH = Path("data/chunking_benchmark.md")
ENCODING = "cl100k_base"


def compare_overlap():
    text = FILE_PATH.read_text(encoding="utf-8")
    tokenizer = tiktoken.get_encoding(ENCODING)

    for overlap in [0, 10, 20]:
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name=ENCODING,
            chunk_size=40,
            chunk_overlap=overlap,
        )

        chunks = splitter.split_text(text)

        total_tokens = sum(
            len(tokenizer.encode(chunk))
            for chunk in chunks
        )

        print(f"\n=== Overlap: {overlap} tokens ===")
        print("Total chunks:", len(chunks))
        print("Total indexed tokens:", total_tokens)

        for index, chunk in enumerate(chunks, start=1):
            print(
                f"Chunk {index}: "
                f"{len(tokenizer.encode(chunk))} tokens"
            )
            print("Start:", repr(chunk[:80]))
            print("End:", repr(chunk[-80:]))


if __name__ == "__main__":
    compare_overlap()
