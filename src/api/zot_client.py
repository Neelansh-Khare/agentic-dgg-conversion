import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class ZotGPTClient:
    """
    Client for interacting with the UCI ZotGPT (Azure OpenAI) API.
    """
    def __init__(self, deployment_id=None, api_version="2023-07-01-preview"):
        self.api_key = os.getenv("ZOTGPT_API_KEY")
        self.base_url = "https://azureapi.zotgpt.uci.edu/openai/deployments"
        self.deployment_id = deployment_id or os.getenv("ZOTGPT_DEPLOYMENT_ID")
        self.api_version = api_version

        if not self.api_key:
            raise ValueError("ZOTGPT_API_KEY environment variable not set.")

    def chat_completion(self, messages, temperature=0.7, max_tokens=1024):
        url = f"{self.base_url}/{self.deployment_id}/chat/completions?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        data = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_embeddings(self, text):
        url = f"{self.base_url}/{self.deployment_id}/embeddings?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        data = {"input": text}
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
