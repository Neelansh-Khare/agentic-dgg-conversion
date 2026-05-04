from abc import ABC, abstractmethod
from src.api.zot_client import ZotGPTClient

class BaseAgent(ABC):
    def __init__(self, client: ZotGPTClient, name: str):
        self.client = client
        self.name = name
        self.system_prompt = self._setup_system_prompt()

    @abstractmethod
    def _setup_system_prompt(self) -> str:
        pass

    def run(self, user_input: str, context: str = ""):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nTask: {user_input}"}
        ]
        return self.client.chat_completion(messages)

class OrchestrationAgent(BaseAgent):
    def _setup_system_prompt(self) -> str:
        return (
            "You are the DGG Orchestration Agent. You are a world-class expert in "
            "Dynamical Graph Grammars (DGGs). Your goal is to coordinate conversions "
            "between mathematical, DGGML, and Mathematica representations. "
            "Ensure that all conversions maintain mathematical invariants of the DGG."
        )

class PureMathAgent(BaseAgent):
    def _setup_system_prompt(self) -> str:
        return (
            "You are the DGG Pure Math Agent. You specialize in LaTeX-style definitions, "
            "graph rewrite rules, and differential equation mappings for DGGs. "
            "Your output should be mathematically rigorous and formatted for academic publication."
        )
