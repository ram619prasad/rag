from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

def fetch_documents(query: str) -> list[Document]:
    embeggings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    
    vector_store = Chroma(
        collection_name="minimal_rag",
        embedding_function=embeggings,
        persist_directory=str(CHROMA_DIR)
    )
    
    results = vector_store.similarity_search(
        query=query,
        k=3
    )   
        
    return results
    

# if __name__ == "__main__":
#     query = (
#         "Which controller manages ReplicaSets "
#         "during rolling updates?"
#     )
    
#     results = fetch_documents(query)
    
#     for rank, (document, distance) in enumerate(
#         results,
#         start=1,
#     ):
#         print(f"\n=== Result {rank} ===")
#         print(f"Chunk ID: {document.metadata.get('chunk_id')}")
#         print(f"Distance: {distance:.4f}")
#         print(f"Source: {document.metadata.get('source')}")
#         print(f"Text:\n{document.page_content}")
    
    
    