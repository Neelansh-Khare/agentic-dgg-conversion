import chromadb
from chromadb.config import Settings
import os

class VectorMemory:
    """
    Manages persistent vector storage for DGG research papers and concept mappings.
    """
    def __init__(self, db_path="./src/memory/vector_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="dgg_knowledge")

    def add_document(self, doc_id, text, metadata=None, embedding=None):
        """
        Adds a document to the vector store.
        Note: Integration with ZotGPT embeddings will be finalized in Phase 2.
        """
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{}],
            ids=[doc_id],
            embeddings=[embedding] if embedding else None
        )

    def query(self, query_text, n_results=3):
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
