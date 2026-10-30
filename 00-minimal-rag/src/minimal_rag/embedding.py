from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
from minimal_rag.chunker import chunk_documents

from dotenv import load_dotenv

load_dotenv()


PARENT = Path(__file__).resolve().parents[2]

CHROMA_DIR = PARENT / "data" / "chroma"


def embed_documents():
    chunks = chunk_documents()
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    
    vector_store = Chroma(
        collection_name="minimal_rag",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    
    existing = vector_store.get(limit=1, include=[])
    
    if not existing["ids"]:
        vector_store.add_documents(
            documents=chunks,
            ids=[chunk.id for chunk in chunks],
        )
        print(f"Indexed {len(chunks)} chunks")
    else:
        print("Reusing existing Chroma index")
        
       
    stored = vector_store.get(limit=3, include=["documents", "metadatas"]) 
    for record_id, text, metadata in zip(
        stored["ids"],
        stored["documents"],
        stored["metadatas"],
    ):
        print(f"\nID: {record_id}")
        print(f"Source: {metadata.get('source')}")
        print(f"Text: {text[:120]}...")

    


if __name__ == "__main__":
    embed_documents()