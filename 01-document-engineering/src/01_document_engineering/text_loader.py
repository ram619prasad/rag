from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from charset_normalizer import from_bytes

SUPPORTED_EXTENSIONS = {".txt", ".md"}

def detect_text_encoding(file_path: str | Path) -> dict:
    path = Path(file_path)
    raw_bytes = path.read_bytes()

    # First, prefer strict UTF-8 decoding.
    try:
        text = raw_bytes.decode("utf-8-sig")

        return {
            "encoding": "utf-8-sig",
            "text": text,
            "detection_method": "utf8_strict",
        }

    except UnicodeDecodeError:
        pass

    # Fall back to heuristic detection.
    matches = from_bytes(raw_bytes)
    best_match = matches.best()

    if best_match is None:
        raise ValueError(
            f"Could not determine a suitable encoding for {path}"
        )

    return {
        "encoding": best_match.encoding,
        "text": str(best_match),
        "detection_method": "heuristic",
    }


def load_text(
    file_path: str | Path,
    encoding: str = "utf-8-sig",
) -> Document:
    path = Path(file_path)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported format: {path.suffix}")

    try:
        content = path.read_text(
            encoding=encoding,
            errors="strict",
        )
    except UnicodeError as exc:
        raise ValueError(
            f"Cannot decode {path} using {encoding}"
        ) from exc

    return Document(
        id=str(path),
        page_content=content,
        metadata={
            "source": str(path),
            "format": path.suffix.lower().lstrip("."),
            "encoding": encoding,
            "encoding_method": "explicit",
        },
    )
    
def load_markdown(path: str | Path) -> list[Document]:
    text = path.read_text(
        encoding="utf-8",
        errors="strict",
    )
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "title"),
            ("##", "section"),
            ("###", "subsection"),
        ],
        strip_headers=False,
    )
    
    documents = splitter.split_text(text)
    for doc in documents:
        doc.metadata["source"] = str(path)
        doc.metadata["format"] = "md"

    return documents

def main():
    path = Path("data/legacy_notes.txt")
    path.write_bytes(
        "The system’s architecture is reliable.".encode("cp1252")
    )

    # Experiment 1: Automatic detection
    result = detect_text_encoding(path)

    print("=== Automatic detection ===")
    print("Detected:", result["encoding"])
    print("Content:", result["text"])

    # Experiment 2: Known correct encoding
    document = load_text(path, encoding="cp1252")

    print("\n=== Explicit encoding ===")
    print("Encoding:", document.metadata["encoding"])
    print("Content:", document.page_content)

    # Experiment 3: Incorrect UTF-8 encoding
    print("\n=== Incorrect encoding ===")

    try:
        load_text(path, encoding="utf-8")
    except ValueError as exc:
        print("Expected error:", exc)
    
    documents = load_markdown(Path("data/engineering_notes.md"))
    for document in documents:
        print(document.page_content)
        print(document.metadata)
    

if __name__ == "__main__":
    main()