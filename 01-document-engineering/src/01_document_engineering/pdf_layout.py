
from pathlib import Path
import pymupdf


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


if __name__ == "__main__":
    inspect_pdf_layout("data/sample.pdf")
