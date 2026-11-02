
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hierarchical_chunker import (
    HierarchicalChunker,
)
from docling_core.transforms.chunker.doc_chunk import (
    DocChunk,
    DocMeta,
)
from docling_core.types.doc.labels import DocItemLabel


FILE_PATH = Path("data/complex_layout.pdf")


def inspect_chunks(chunks: list) -> None:
    table_chunk_count = 0

    print("\n=== Hierarchical Chunks ===")
    print("Total chunks:", len(chunks))

    for index, base_chunk in enumerate(chunks, start=1):

        # Narrow BaseChunk to DocChunk for Pylance.
        if not isinstance(base_chunk, DocChunk):
            continue

        meta = base_chunk.meta

        if not isinstance(meta, DocMeta):
            continue

        print(f"\n{'=' * 60}")
        print(f"CHUNK {index}")
        print("=" * 60)

        # 1. Heading metadata
        print("Headings:", meta.headings or [])

        # 2. Chunk size
        print("Characters:", len(base_chunk.text))

        # 3. Source document element types
        labels = [
            item.label.value
            for item in meta.doc_items
        ]

        print("Element types:", labels)

        # 4. Source page numbers
        pages = sorted({
            prov.page_no
            for item in meta.doc_items
            for prov in (item.prov or [])
        })

        print("Source pages:", pages)

        # 5. Preview content
        print("Content preview:", repr(base_chunk.text[:200]))

        # 6. Identify table-containing chunks
        table_items = [
            item
            for item in meta.doc_items
            if item.label == DocItemLabel.TABLE
        ]

        if not table_items:
            continue

        table_chunk_count += 1

        print("\n--- TABLE CONTENT ---")
        print(base_chunk.text)

        # 7. Table provenance
        for item in table_items:
            for prov in (item.prov or []):
                print("\nTable page:", prov.page_no)
                print("Bounding box:", prov.bbox)

    print("\n=== Summary ===")
    print("Total chunks:", len(chunks))
    print("Table-containing chunks:", table_chunk_count)


def run_hierarchical_chunking() -> None:
    if not FILE_PATH.is_file():
        raise FileNotFoundError(
            f"PDF not found: {FILE_PATH}"
        )

    print("Converting:", FILE_PATH)

    # 1. Parse the PDF
    converter = DocumentConverter()
    result = converter.convert(FILE_PATH)

    document = result.document

    print("Tables detected:", len(document.tables))

    # 2. Generate hierarchical chunks
    chunker = HierarchicalChunker()

    chunks = list(
        chunker.chunk(dl_doc=document)
    )

    # 3. Inspect results
    inspect_chunks(chunks)


if __name__ == "__main__":
    run_hierarchical_chunking()
