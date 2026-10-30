
from pathlib import Path

import pymupdf


def classify_page(text_length: int, image_count: int) -> str:
    if text_length == 0 and image_count > 0:
        return "possible_scanned_page"

    if text_length == 0:
        return "empty_or_graphics_only"

    if text_length < 100 and image_count > 0:
        return "image_heavy"

    if image_count > 0:
        return "mixed_content"

    return "text_only"


from pathlib import Path
import pymupdf


def safe_inspect_pdf(file_path: Path) -> dict:
    file_path = Path(file_path)

    if not file_path.is_file():
        return {
            "success": False,
            "result": None,
            "error": "PDF file does not exist or is not a regular file",
        }

    try:
        return {
            "success": True,
            "result": inspect_pdf(file_path),
            "error": None,
        }

    except (pymupdf.FileDataError, pymupdf.EmptyFileError) as exc:
        return {
            "success": False,
            "result": None,
            "error": f"Invalid PDF: {exc}",
        }

    except ValueError as exc:
        return {
            "success": False,
            "result": None,
            "error": str(exc),
        }


def inspect_pdf(file_path: Path) -> dict:
    with pymupdf.open(file_path) as pdf:
        if pdf.needs_pass:
            raise ValueError("PDF requires a password")
        
        pages = []

        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            classification = classify_page(
                text_length=len(text.strip()),
                image_count=len(page.get_image_info()),
            )

            pages.append({
                "page_number": page_number,
                "text_length": len(text.strip()),
                "image_count": len(page.get_image_info()),
                "has_text": bool(text.strip()),
                "preview": text[:300],
                "classification": classification
            })

        return {
            "filename": file_path.name,
            "page_count": len(pdf),
            "pages": pages,
        }


def main():
    file_path = Path("data/sample.pdf")
    validation = safe_inspect_pdf(file_path)
    
    if validation['success']:
        result = validation['result']

        print("Filename:", result["filename"])
        print("Total pages:", result["page_count"])

        for page in result["pages"]:
            print(
                f"Page {page['page_number']}: "
                f"Text={page['text_length']} chars, "
                f"Images={page['image_count']}, "
                f"Has text={page['has_text']} "
                f"Preview={page['preview']} "
                f"Classification={page['classification']} "
            )      
    else:
        print(validation['error'])


if __name__ == "__main__":
    main()
