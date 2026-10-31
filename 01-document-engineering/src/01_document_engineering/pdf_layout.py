
from pathlib import Path
import pymupdf

def inspect_table_layout(file_path: str | Path) -> None:
    with pymupdf.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            lines = [
                line.strip()
                for line in page.get_text("text", sort=True).splitlines()
                if line.strip()
            ]

            print(f"\nPage {page_number}")
            print("First lines:", lines[:3])
            print("Last lines:", lines[-3:])
        
    with pymupdf.open(file_path) as pdf:
        page = pdf[2]

        finder = page.find_tables()

        for table in finder.tables:
            print("Header names:", table.header.names)
            print("Header external:", table.header.external)
            print("Header bbox:", table.header.bbox)
            print("Table bbox:", table.bbox)

            print("\nExtracted rows:")
            for row in table.extract():
                print(row)

def inspect_pdf_layout(file_path: str | Path) -> None:
    with pymupdf.open(file_path) as pdf:
        page = pdf[0]

        print("Page dimensions:", page.rect)
        
        print("\n=== Original extraction order ===")
        print(page.get_text("text", sort=False)[:1000])

        print("\n=== Position-sorted extraction ===")
        print(page.get_text("text", sort=True)[:1000])

        blocks = page.get_text("blocks")

        for block in blocks:
            x0, y0, x1, y1, text, block_number, block_type = block

            if block_type != 0:
                continue

            print(f"\nBlock: {block_number}")
            print(f"Bounding box: {(x0, y0, x1, y1)}")
            print(f"Text: {text[:150]!r}")
            
            
        data = page.get_text("dict")

        for block in data["blocks"]:
            if block["type"] != 0:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    print({
                        "text": span["text"][:60],
                        "font": span["font"],
                        "size": span["size"],
                        "bbox": span["bbox"],
                    })
                    
        
        content_area = pymupdf.Rect(
            0,
            0,
            page.rect.width,
            page.rect.height - 60,
        )

        text = page.get_text(
            "text",
            clip=content_area,
            sort=True,
        )

        print(text[:300])
        print("Contains page number at beginning:", text.lstrip().startswith("1"))


def inspect_complex_pdf(file_path: str | Path) -> None:
    with pymupdf.open(file_path) as pdf:
        page = pdf[1]  # The deliberately challenging second page

        print("=== Original order ===")
        print(page.get_text("text", sort=False)[:1500])

        print("\n=== Sorted order ===")
        print(page.get_text("text", sort=True)[:1500])
    
if __name__ == "__main__":
    # inspect_pdf_layout("data/sample.pdf")
    # inspect_complex_pdf("data/complex_layout.pdf")
    inspect_table_layout("data/complex_layout.pdf")
    
    
    # import pymupdf4llm

    # markdown = pymupdf4llm.to_markdown(
    #     "data/complex_layout.pdf",
    #     pages=[1],  # Zero-based: second page
    #     use_ocr=False,
    # )
    
    # print(repr(markdown[:1500]))

    # print(markdown)
    
    # headings = [
    #     "3. Detection & Triage",
    #     "3.1 Diagnostic signals",
    #     "4. Recovery Actions",
    #     "4.1 Validation",
    # ]

    # for heading in headings:
    #     position = markdown.find(heading)
    #     print(f"{heading}: position={position}")

