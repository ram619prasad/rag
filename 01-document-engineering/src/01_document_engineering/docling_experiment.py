
from pathlib import Path
from time import perf_counter
from html import unescape

from docling.document_converter import DocumentConverter


def inspect_with_docling(file_path: str | Path) -> None:
    path = Path(file_path)

    converter = DocumentConverter()

    start = perf_counter()
    result = converter.convert(path)
    elapsed = perf_counter() - start

    document = result.document
    markdown = document.export_to_markdown()

    print("Conversion status:", result.status)
    print(f"Conversion time: {elapsed:.2f} seconds")
    print("Tables detected:", len(document.tables))

    print("\n=== Extracted Markdown ===")
    print(markdown)
    
    normalized_markdown = unescape(markdown)

    headings = [
        "3. Detection & Triage",
        "3.1 Diagnostic signals",
        "4. Recovery Actions",
        "4.1 Validation",
    ]

    positions = [
        normalized_markdown.find(heading)
        for heading in headings
    ]

    for heading, position in zip(headings, positions):
        print(f"{heading}: {position}")

    correct_order = (
        all(position >= 0 for position in positions)
        and positions == sorted(positions)
    )

    print("Heading order correct:", correct_order)
    
    for index, table in enumerate(document.tables, start=1):
        print(f"\n=== Table {index} ===")

        print("Rows:", table.data.num_rows)
        print("Columns:", table.data.num_cols)

        for provenance in table.prov:
            print("Page:", provenance.page_no)
            print("Bounding box:", provenance.bbox)

    # # Save output for comparison with other parsers.
    # output_path = Path("data/docling_output.md")
    # output_path.write_text(markdown, encoding="utf-8")
    
    markers = [
        "Page two should be read from the LEFT COLUMN first",
        "Start with request correlation IDs",
        "Look for HTTP 5xx trends",
        "Triage step A",
        "If the database primary is unavailable",
        "Recovery step A",
        "After recovery, compare transaction counts",
        "Success criterion",
    ]

    positions = [normalized_markdown.find(m) for m in markers]

    for marker, position in zip(markers, positions):
        print(f"{position:5} | {marker}")

    passed = (
        all(position >= 0 for position in positions)
        and positions == sorted(positions)
    )

    print("Paragraph reading order correct:", passed)


if __name__ == "__main__":
    inspect_with_docling("data/complex_layout.pdf")
