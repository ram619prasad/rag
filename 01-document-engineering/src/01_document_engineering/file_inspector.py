from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".md",
    ".txt",
    ".html",
    ".docx",
}

def validate_file(file_path: Path) -> str | None:
    if not file_path.exists():
        return "File does not exist"

    if not file_path.is_file():
        return "Path is not a regular file"

    if file_path.stat().st_size == 0:
        return "File is empty"

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return "Unsupported extension"

    return None

def inspect_file(file_path: Path) -> dict:
    file_path = Path(file_path)
    error = validate_file(file_path)
    
    return {
        "name": str(file_path.stem),
        "extension": file_path.suffix,
        "size_bytes": (
            file_path.stat().st_size
            if file_path.is_file()
            else 0
        ),
        "is_valid": error is None,
        "error": error,
    }