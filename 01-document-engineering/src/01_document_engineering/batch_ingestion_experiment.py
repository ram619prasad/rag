
import hashlib
import json
import os
import tempfile
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionStatus
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)

import logging


DATA_DIR = Path("data")
OUTPUT_DIR = Path(".ingestion_output")
MANIFEST_PATH = Path(".ingestion_manifest.json")

PIPELINE_VERSION = "docling-v1"

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".html"
}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# 1. Discover documents
def discover_documents(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


# 2. Calculate fingerprint
def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


# 3. Load existing manifest
def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}

    return json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8")
    )


# 4. Write files atomically
def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)

        os.replace(temporary_path, path)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


# 5. Retry ONLY transient storage errors
@retry(
    retry=retry_if_exception_type(
        (BlockingIOError, TimeoutError)
    ),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def save_with_retry(path: Path, content: str) -> None:
    atomic_write(path, content)


# 6. Stable output path per source
def output_path_for(source: str) -> Path:
    source_id = hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()[:20]

    return OUTPUT_DIR / f"{source_id}.md"


# 7. Convert using Docling
def process_document(
    path: Path,
    converter: DocumentConverter,
) -> tuple[str, int]:
    result = converter.convert(
        path,
        raises_on_error=False,
    )

    if result.status != ConversionStatus.SUCCESS:
        raise ValueError(
            f"Conversion status: {result.status}"
        )

    markdown = result.document.export_to_markdown()

    if not markdown.strip():
        raise ValueError("No content extracted")

    return markdown, len(result.document.tables)


# 8. Batch processing with checkpointing
def process_batch(documents: list[Path]) -> list[dict]:
    converter = DocumentConverter()
    manifest = load_manifest()

    results = []

    for path in documents:
        source = str(path.resolve())
        output_path = output_path_for(source)

        try:
            current_hash = fingerprint(path)

            expected_state = {
                "hash": current_hash,
                "pipeline_version": PIPELINE_VERSION,
            }

            # Skip only if the document was processed
            # AND its extracted output still exists.
            if (
                manifest.get(source) == expected_state
                and output_path.is_file()
            ):
                results.append({
                    "source": str(path),
                    "status": "skipped",
                })
                continue

            print(f"\nProcessing: {path}")

            markdown, table_count = process_document(
                path, converter
            )

            # Persist extracted content first.
            save_with_retry(output_path, markdown)

            # Checkpoint only after output is saved.
            updated_manifest = {
                **manifest,
                source: expected_state,
            }

            save_with_retry(
                MANIFEST_PATH,
                json.dumps(updated_manifest, indent=2),
            )

            manifest = updated_manifest

            results.append({
                "source": str(path),
                "status": "success",
                "characters": len(markdown),
                "tables": table_count,
            })

        except Exception as exc:
            # Do not mark this attempt as successful.
            # A previous checkpoint remains untouched.
            results.append({
                "source": str(path),
                "status": "failed",
                "error": str(exc),
            })

    return results


# 9. Summary
def print_summary(results: list[dict]) -> None:
    print("\n=== Batch Results ===")

    for result in results:
        print(result)

    print("\n=== Summary ===")
    print("Discovered:", len(results))

    for status in ["success", "skipped", "failed"]:
        count = sum(
            result["status"] == status
            for result in results
        )
        print(f"{status.capitalize()}: {count}")


def main():
    documents = discover_documents(DATA_DIR)
    results = process_batch(documents)

    print_summary(results)


if __name__ == "__main__":
    main()
