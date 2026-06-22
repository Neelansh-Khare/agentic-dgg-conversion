import os
import requests
from dotenv import load_dotenv

load_dotenv()

class OllamaClient:
    """
    Client for interacting with a local Ollama instance.
    Exposes the same interface as ZotGPTClient for drop-in use.
    """
    def __init__(self, model=None, embedding_model=None, base_url=None):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.embedding_model = embedding_model or os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    def chat_completion(self, messages, temperature=0.7, max_tokens=1024):
        url = f"{self.base_url}/api/chat"
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        raw = response.json()
        # Translate Ollama shape → OpenAI shape that the agents expect
        return {"choices": [{"message": {"content": raw["message"]["content"]}}]}

    def get_embeddings(self, text):
        url = f"{self.base_url}/api/embeddings"
        data = {"model": self.embedding_model, "prompt": text}
        response = requests.post(url, json=data)
        response.raise_for_status()
        raw = response.json()
        # Translate Ollama shape → OpenAI shape that VectorMemory expects
        return {"data": [{"embedding": raw["embedding"]}]}
