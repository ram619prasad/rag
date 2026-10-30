from pathlib import Path
from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def get_documents() -> list[Document]:
    file_path = PROJECT_ROOT / "data" / "kubernetes_hpa.md"

    document = Document(
        page_content=file_path.read_text(encoding="utf-8"),
        metadata={"source": str(file_path)}
    )

    return [document]


def main():
    documents = get_documents()
    print("Documents loaded:", len(documents))

    for doc in documents:
        print("Characters:", len(doc.page_content))
        print("Source:", doc.metadata["source"])
        print("Preview:", doc.page_content[:200])
        

if __name__ == "__main__":
    main()