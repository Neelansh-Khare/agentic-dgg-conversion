import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.api.zot_client import ZotGPTClient
from src.memory.vector_memory import VectorMemory

def ingest_papers(papers_dir="base_documents"):
    """
    Scans the base_documents directory and ingests PDF and text content.
    Includes chunking and embedding generation via ZotGPT.
    """
    client = ZotGPTClient()
    memory = VectorMemory()
    
    # Configure text splitter for DGG papers
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )

    if not os.path.exists(papers_dir):
        print(f"Directory {papers_dir} not found. Creating it...")
        os.makedirs(papers_dir)
        return

    for filename in os.listdir(papers_dir):
        path = os.path.join(papers_dir, filename)
        content = ""

        if filename.endswith(".pdf"):
            print(f"Processing PDF: {filename}")
            try:
                reader = PdfReader(path)
                for page in reader.pages:
                    content += page.extract_text() + "\n"
            except Exception as e:
                print(f"Failed to read PDF {filename}: {e}")
                continue
        
        elif filename.endswith(".txt"):
            print(f"Processing Text: {filename}")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        
        else:
            continue

        if content:
            # Chunk the content
            chunks = text_splitter.split_text(content)
            print(f"Split {filename} into {len(chunks)} chunks.")

            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_chunk_{i}"
                
                # Get embeddings from ZotGPT
                try:
                    embedding_response = client.get_embeddings(chunk)
                    # Note: Azure OpenAI returns embeddings in ['data'][0]['embedding']
                    embedding = embedding_response['data'][0]['embedding']
                    
                    # Add to vector memory
                    memory.add_document(
                        doc_id=chunk_id,
                        text=chunk,
                        metadata={"source": filename, "chunk_index": i},
                        embedding=embedding
                    )
                except Exception as e:
                    print(f"Failed to process chunk {i} of {filename}: {e}")
            
            print(f"Successfully ingested {filename}")

if __name__ == "__main__":
    print("Starting ingestion process...")
    ingest_papers()
    print("Ingestion complete.")
