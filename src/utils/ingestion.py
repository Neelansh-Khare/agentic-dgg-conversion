import os
from src.api.zot_client import ZotGPTClient
from src.memory.vector_memory import VectorMemory

def ingest_papers(papers_dir="base_documents"):
    """
    Scans the base_documents directory and ingests content into vector memory.
    Note: For PDF processing, additional libraries like PyMuPDF or LangChain PDFLoaders 
    would be added here in a future step.
    """
    client = ZotGPTClient()
    memory = VectorMemory()
    
    if not os.path.exists(papers_dir):
        print(f"Directory {papers_dir} not found.")
        return

    for filename in os.listdir(papers_dir):
        if filename.endswith(".txt"): # Starting with text support
            path = os.path.join(papers_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            print(f"Ingesting {filename}...")
            # In a full Phase 2 implementation, we would chunk the text here
            # and use client.get_embeddings(chunk)
            memory.add_document(doc_id=filename, text=content)
            print(f"Successfully ingested {filename}")

if __name__ == "__main__":
    # This script is a placeholder to be expanded during Phase 2
    print("Ingestion script ready.")
