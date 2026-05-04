import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.api.zot_client import ZotGPTClient
from src.memory.vector_memory import VectorMemory

def ingest_papers(base_dir="base_documents"):
    """
    Scans nested directories in base_documents and ingests content.
    Metadata 'agent_scope' is used to filter context for specific agents.
    """
    client = ZotGPTClient()
    memory = VectorMemory()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )

    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} not found.")
        return

    # Iterate through agent-specific subdirectories
    for agent_dir in os.listdir(base_dir):
        agent_path = os.path.join(base_dir, agent_dir)
        if not os.path.isdir(agent_path):
            continue

        print(f"Ingesting documents for scope: {agent_dir}")
        
        for filename in os.listdir(agent_path):
            file_path = os.path.join(agent_path, filename)
            content = ""

            if filename.endswith(".pdf"):
                try:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
                except Exception as e:
                    print(f"Error reading PDF {filename}: {e}")
            
            elif filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            if content:
                chunks = text_splitter.split_text(content)
                for i, chunk in enumerate(chunks):
                    try:
                        # Get embeddings
                        embedding = client.get_embeddings(chunk)['data'][0]['embedding']
                        
                        # Add to memory with AGENT_SCOPE metadata
                        memory.add_document(
                            doc_id=f"{agent_dir}_{filename}_chunk_{i}",
                            text=chunk,
                            metadata={
                                "source": filename, 
                                "agent_scope": agent_dir, # Critical for filtering
                                "chunk_index": i
                            },
                            embedding=embedding
                        )
                    except Exception as e:
                        print(f"Failed chunk {i} of {filename}: {e}")
                print(f"Done: {filename}")

if __name__ == "__main__":
    ingest_papers()
