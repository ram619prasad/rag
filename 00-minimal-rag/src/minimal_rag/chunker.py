from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document

from minimal_rag.loader import get_documents

def chunk_documents() -> list[Document]:
    # Step 1: Load original documents
    documents = get_documents()

    # Step 2: Create LangChain text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    # Step 3: Split documents into chunks
    chunks = splitter.split_documents(documents)

    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks):
        source = Path(chunk.metadata["source"]).stem
        chunk.id = f"{source}_chunk:{index:03d}"
        chunk.metadata["chunk_id"] = chunk.id
            
            
    return chunks
