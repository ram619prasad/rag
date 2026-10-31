
import re
from html import unescape
from textwrap import dedent
import hashlib
from pathlib import Path

from langchain_core.documents import Document
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DocItemLabel


def normalize_text(text: str, decode_html: bool = False) -> str:
    # Decode HTML entities only for sources that need it.
    if decode_html:
        text = unescape(text)

    # Standardize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces from lines.
    lines = [line.rstrip() for line in text.split("\n")]

    text = "\n".join(lines)

    # Reduce three or more consecutive newlines to two.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_page_metadata(metadata: dict, parser: str) -> dict:
    if parser == "pymupdf":
        page_number = metadata["page_index"] + 1
    elif parser == "docling":
        page_number = metadata["page_no"]
    else:
        raise ValueError(f"Unsupported parser: {parser}")

    if page_number < 1:
        raise ValueError("Page numbers must be one-based")

    return {
        "source": metadata["source"],
        "parser": parser,
        "page_number": page_number,
    }
    
def content_fingerprint(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def file_fingerprint(path: str) -> str:
    return content_fingerprint(Path(path).read_bytes())

def inspect_headers_footers(file_path: str) -> None:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    converter = DocumentConverter()
    result = converter.convert(path)
    document = result.document

    print(f"\nDocument: {path.name}")
    print("=" * 60)

    header_count = 0
    footer_count = 0

    for item in document.texts:
        if item.label not in {
            DocItemLabel.PAGE_HEADER,
            DocItemLabel.PAGE_FOOTER,
        }:
            continue

        pages = [prov.page_no for prov in item.prov]

        print(f"Label: {item.label}")
        print(f"Pages: {pages}")
        print(f"Text: {item.text!r}")
        print("-" * 60)

        if item.label == DocItemLabel.PAGE_HEADER:
            header_count += 1
        else:
            footer_count += 1

    print("\n=== Summary ===")
    print(f"Headers detected: {header_count}")
    print(f"Footers detected: {footer_count}")


def test_content_changes():
    document_id = "payment-service-runbook"

    original = b"Database: PostgreSQL\nReplicas: 3"
    updated = b"Database: PostgreSQL\nReplicas: 5"

    original_hash = content_fingerprint(original)
    updated_hash = content_fingerprint(updated)

    print("Document ID:", document_id)
    print("Original hash:", original_hash)
    print("Updated hash: ", updated_hash)

    print("Content changed:", original_hash != updated_hash)

def text_normalize_metadata():
    pymupdf_metadata = {
        "source": "data/complex_layout.pdf",
        "page_index": 2,
    }

    docling_metadata = {
        "source": "data/complex_layout.pdf",
        "page_no": 3,
    }
    
    pymupdf_result = normalize_page_metadata(
    pymupdf_metadata, "pymupdf"
)

    docling_result = normalize_page_metadata(
        docling_metadata, "docling"
    )

    print("PyMuPDF:", pymupdf_result)
    print("Docling:", docling_result)

    assert pymupdf_result["page_number"] == docling_result["page_number"]
    print("Page numbers match!")


def main():
    raw_text = dedent("""
    ## Storage &amp; Reliability

    Database: PostgreSQL
    Replicas: 3

    Recovery time: 15 minutes
""")

    normalized = normalize_text(raw_text, decode_html=True)

    document = Document(
        page_content=normalized,
        metadata={
            "source": "data/complex_layout.pdf",
            "format": "pdf",
            "parser": "docling",
            "page_number": 1,
            "content_type": "text",
            "extraction_version": "1",
        },
    )

    print("=== NORMALIZED CONTENT ===")
    print(document.page_content)

    print("\n=== METADATA ===")
    print(document.metadata)


if __name__ == "__main__":
    # main()
    # text_normalize_metadata()
    # test_content_changes()
    inspect_headers_footers("data/complex_layout.pdf")