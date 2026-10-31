
from pathlib import Path
import pymupdf


def create_mixed_pdf():
    with pymupdf.open("data/scanned_incident.pdf") as scanned:
        scanned_pix = scanned[0].get_pixmap(dpi=150)

        with pymupdf.open() as output:
            page = output.new_page(width=595, height=842)

            # Existing selectable text
            page.insert_text(
                (50, 60),
                "Incident Review: Payment Service",
                fontsize=18,
            )

            page.insert_text(
                (50, 90),
                "The incident details appear in the image below.",
                fontsize=11,
            )

            # Scanned image containing text
            page.insert_image(
                pymupdf.Rect(50, 130, 545, 790),
                stream=scanned_pix.tobytes("png"),
            )

            output.save("data/mixed_incident.pdf")

def create_scanned_pdf(output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Create a page containing real text.
    source = pymupdf.open()
    page = source.new_page(width=595, height=842)

    lines = [
        "Payment Service Incident Report",
        "Incident ID: INC-2026-1042",
        "Database: PostgreSQL",
        "Affected replicas: 3",
        "Recovery time: 15 minutes",
    ]

    for index, line in enumerate(lines):
        page.insert_text(
            (50, 80 + index * 45),
            line,
            fontsize=17,
        )

    # Step 2: Render the text into pixels.
    pixmap = page.get_pixmap(dpi=200, alpha=False)

    # Step 3: Create a new PDF containing only the image.
    scanned = pymupdf.open()
    scanned_page = scanned.new_page(width=595, height=842)

    scanned_page.insert_image(
        scanned_page.rect,
        stream=pixmap.tobytes("png"),
    )

    scanned.save(output_path)

    scanned.close()
    source.close()

def compare_ocr(file_path: str | Path) -> None:
    with pymupdf.open(file_path) as pdf:
        page = pdf[0]

        print("=== Normal extraction ===")
        print(repr(page.get_text("text")))

        print("\n=== OCR extraction ===")
        text_page = page.get_textpage_ocr(
            language="eng",
            dpi=200,
            full=True,
        )

        print(page.get_text("text", textpage=text_page))
        

def selective_ocr():
    with pymupdf.open("data/mixed_incident.pdf") as pdf:
        page = pdf[0]

        print("=== Normal ===")
        print(page.get_text("text"))

        print("\n=== Partial OCR ===")
        text_page = page.get_textpage_ocr(
            language="eng",
            dpi=200,
            full=False,
        )
        print(page.get_text("text", textpage=text_page))

if __name__ == "__main__":
    # path = "data/scanned_incident.pdf"
    # create_scanned_pdf(path)
    # print("Created data/scanned_incident.pdf")
    # compare_ocr(path)
    
    # create_mixed_pdf()
    selective_ocr()
