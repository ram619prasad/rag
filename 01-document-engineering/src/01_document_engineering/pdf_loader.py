
from pathlib import Path
from collections.abc import Iterator

import pymupdf
from langchain_core.documents import Document
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

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

def _create_document(pdf, page_number, page, file_path) -> Document:
    text = page.get_text("text")
    image_count = len(page.get_image_info())
    classification = classify_page(
        text_length=len(text.strip()),
        image_count=image_count,
    )
                
    metadata = {
        "source": str(file_path),
        "page": page_number,
        "total_pages": pdf.page_count,
        "format": "pdf",
        "image_count": image_count,
        "classification": classification,
    }

    return Document(
        id=f"{metadata['source']}:page:{page_number}",
        page_content=text,
        metadata=metadata
    )
    

def lazy_load_pdf(file_path: Path) -> Iterator[Document]:
    with pymupdf.open(file_path) as pdf:
        if pdf.needs_pass:
            raise ValueError("PDF requires a password")

        for page_number, page in enumerate(pdf, start=1):
            yield _create_document(pdf, page_number, page, file_path)


def load_pdf(file_path: Path) -> list[Document]:
    documents = []

    with pymupdf.open(file_path) as pdf:
        if pdf.needs_pass:
            raise ValueError("PDF requires a password")

        for page_number, page in enumerate(pdf, start=1):
            doc = _create_document(pdf, page_number, page, file_path)
            documents.append(doc)

    return documents


def main():
    documents = load_pdf("data/sample.pdf")
    
    for page_number, page in enumerate(documents, start=1):
        print(f"Document: {page_number}")
        print(f"ID: {page.id}")
        print(f"Page: {page.metadata['page']}")
        print(f"Content length: {len(page.page_content)}")
        print(f"Image count: {page.metadata['image_count']}")
        print(f"Classification: {page.metadata['classification']}")
    
    print("Eager loading")
    documents = load_pdf("data/sample.pdf")
    print("Loaded:", len(documents))

    print("\nLazy loading")
    documents = lazy_load_pdf("data/sample.pdf")
    print("Object:", type(documents))

    for document in documents:
        print(
            document.metadata["page"],
            len(document.page_content),
            document.metadata["classification"],
        )
        
    loader = PyMuPDF4LLMLoader(
        file_path="data/sample.pdf",
        mode="page",
    )

    documents = loader.load()

    for doc in documents:
        print("Metadata:", doc.metadata)
        print("Characters:", len(doc.page_content))
        print("Preview:", doc.page_content[:150])
            
        

if __name__ == "__main__":
    main()
    