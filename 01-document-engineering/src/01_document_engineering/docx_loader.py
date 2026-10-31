
from pathlib import Path

from docx import Document as WordDocument
from docx.table import Table
from docx.text.paragraph import Paragraph
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
)
from langchain_community.document_loaders import Docx2txtLoader

def load_docx(file_path: str | Path) -> Document:
    path = Path(file_path)
    word_doc = WordDocument(str(path))

    parts = []

    for element in word_doc.iter_inner_content():
        if isinstance(element, Paragraph):
            text = element.text.strip()

            if not text:
                continue

            if element.style.name.startswith("Heading "):
                level = int(element.style.name.split()[-1])
                parts.append(f"{'#' * level} {text}")
            else:
                parts.append(text)

        elif isinstance(element, Table):
            rows = [
                [cell.text.strip() for cell in row.cells]
                for row in element.rows
            ]

            if rows:
                header = rows[0]
                parts.append(
                    "| " + " | ".join(header) + " |"
                )
                parts.append(
                    "| " + " | ".join(["---"] * len(header)) + " |"
                )

                for row in rows[1:]:
                    parts.append(
                        "| " + " | ".join(row) + " |"
                    )

    return Document(
        id=str(path),
        page_content="\n\n".join(parts),
        metadata={
            "source": str(path),
            "format": "docx",
        },
    )


if __name__ == "__main__":
    # document = load_docx("data/payment_service.docx")
    # print(document.page_content)
    # print("\nMetadata:", document.metadata)
    
    # loader = Docx2txtLoader("data/payment_service.docx")
    # documents = loader.load()
    # for doc in documents:
    #     print("Content:")
    #     print(doc.page_content)
    #     print("\nMetadata:", doc.metadata)
    
    loader = UnstructuredWordDocumentLoader(
        "data/payment_service.docx",
        mode="elements",
    )

    documents = loader.load()

    print("Total elements:", len(documents))

    for doc in documents:
        print("\nCategory:", doc.metadata.get("category"))
        print("Content:", doc.page_content)
        print("Metadata:", doc.metadata)