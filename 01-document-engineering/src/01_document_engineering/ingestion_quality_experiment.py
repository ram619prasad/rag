
from docling.document_converter import DocumentConverter
from html import unescape
from jiwer import wer, cer
import pandas as pd
from pathlib import Path


EXPECTED_LINES = [
    "Payment Service Incident Report",
    "Incident ID: INC-2026-1042",
    "Database: PostgreSQL",
    "Affected replicas: 3",
    "Recovery time: 15 minutes",
]

EXPECTED_ORDER = [
    "Page two should be read from the LEFT COLUMN first",
    "Start with request correlation IDs",
    "Look for HTTP 5xx trends",
    "Triage step A",
    "If the database primary is unavailable",
    "Recovery step A",
    "After recovery, compare transaction counts",
    "Success criterion",
]


EXPECTED_TABLE = pd.DataFrame(
    [
        ["Payments", "PostgreSQL", "3", "12", "FinTech"],
        ["Orders", "MongoDB", "2", "10", "Commerce"],
        ["Inventory", "MySQL", "2", "8", "Supply"],
        ["Search", "OpenSearch", "3", "16", "Platform"],
        ["Notifications", "Redis", "2", "7", "Messaging"],
    ],
    columns=[
        "Service",
        "Datastore",
        "Min pods",
        "Max pods",
        "Owner",
    ],
)


EXPECTED_OCR_TEXT = """Payment Service Incident Report
Incident ID: INC-2026-1042
Database: PostgreSQL
Affected replicas: 3
Recovery time: 15 minutes"""


def evaluate_ocr_error_rate(converter):
    result = converter.convert("data/scanned_incident.pdf")

    extracted = result.document.export_to_markdown().strip()

    # Normalize line breaks for this controlled experiment.
    reference = " ".join(EXPECTED_OCR_TEXT.split())
    hypothesis = " ".join(extracted.split())

    print("\n=== OCR Error Rate ===")
    print(f"WER: {wer(reference, hypothesis):.2%}")
    print(f"CER: {cer(reference, hypothesis):.2%}")

    print("\nExtracted text:")
    print(extracted)



def evaluate_table_accuracy(converter):
    result = converter.convert("data/complex_layout.pdf")
    document = result.document

    if len(document.tables) != 1:
        print("Expected one table, found:", len(document.tables))
        return

    actual = document.tables[0].export_to_dataframe(doc=document)

    # Normalize data types and harmless surrounding whitespace.
    actual = actual.astype(str).map(str.strip)
    expected = EXPECTED_TABLE.astype(str).map(str.strip)

    headers_correct = actual.columns.tolist() == expected.columns.tolist()
    shape_correct = actual.shape == expected.shape

    print("\n=== Table Quality ===")
    print("Expected shape:", expected.shape)
    print("Actual shape:", actual.shape)
    print("Headers correct:", headers_correct)

    if shape_correct and headers_correct:
        matched_cells = (actual == expected).to_numpy().sum()
    else:
        matched_cells = 0

    total_cells = expected.size
    accuracy = matched_cells / total_cells

    print(f"Cell accuracy: {accuracy:.1%}")
    print("Exact table match:", actual.equals(expected))

    if not actual.equals(expected):
        print("\nActual table:")
        print(actual.to_string(index=False))


def evaluate_reading_order(
    extracted_text: str,
    expected_markers: list[str],
) -> dict:
    text = unescape(extracted_text)

    positions = [
        text.find(marker)
        for marker in expected_markers
    ]

    missing = [
        marker
        for marker, position in zip(expected_markers, positions)
        if position == -1
    ]

    # All markers must exist and be in strict order.
    passed = (
        not missing
        and all(
            earlier < later
            for earlier, later in zip(
                positions, positions[1:]
            )
        )
    )

    return {
        "passed": passed,
        "positions": positions,
        "missing": missing,
    }


def evaluate_complex_pdf(converter):
    result = converter.convert(
        "data/complex_layout.pdf"
    )

    markdown = result.document.export_to_markdown()

    evaluation = evaluate_reading_order(
        markdown,
        EXPECTED_ORDER,
    )

    print("\n=== Reading Order Quality ===")

    for marker, position in zip(
        EXPECTED_ORDER,
        evaluation["positions"],
    ):
        print(f"{position:5} | {marker}")

    print("Missing:", evaluation["missing"])
    print("Reading order correct:", evaluation["passed"])


def evaluate_completeness(
    extracted_text: str,
    expected_lines: list[str],
) -> dict:
    found = [
        line for line in expected_lines
        if line in extracted_text
    ]

    missing = [
        line for line in expected_lines
        if line not in extracted_text
    ]

    return {
        "expected": len(expected_lines),
        "found": len(found),
        "coverage": len(found) / len(expected_lines),
        "missing": missing,
    }
    
def evaluate_provenance(converter):
    source = Path("data/complex_layout.pdf")

    result = converter.convert(source)
    document = result.document

    print("\n=== Provenance Quality ===")

    if len(document.tables) != 1:
        print("Provenance correct: False")
        print("Reason: Expected exactly one table")
        return

    table = document.tables[0]

    if not table.prov:
        print("Provenance correct: False")
        print("Reason: Table has no provenance")
        return

    provenance = table.prov[0]
    bbox = provenance.bbox

    # Bounds are expressed in the original page
    # coordinate system, with bottom-left origin.
    page_number_correct = provenance.page_no == 3

    bbox_valid = (
        bbox.l < bbox.r
        and bbox.b < bbox.t
    )

    print("Source:", source)
    print("Page:", provenance.page_no)
    print("Bounding box:", bbox)
    print("Page number correct:", page_number_correct)
    print("Bounding box valid:", bbox_valid)

    print(
        "Provenance correct:",
        page_number_correct and bbox_valid,
    )


def main():
    converter = DocumentConverter()

    result = converter.convert(
        "data/scanned_incident.pdf"
    )

    # markdown = result.document.export_to_markdown()
    # evaluate_complex_pdf(converter)
    # evaluate_table_accuracy(converter)
    # evaluate_ocr_error_rate(converter)
    evaluate_provenance(converter)

    # evaluation = evaluate_completeness(
    #     markdown,
    #     EXPECTED_LINES,
    # )

    # print("=== Extraction Quality ===")
    # print("Expected lines:", evaluation["expected"])
    # print("Found lines:", evaluation["found"])
    # print(f"Coverage: {evaluation['coverage']:.1%}")
    # print("Missing:", evaluation["missing"])


if __name__ == "__main__":
    main()
