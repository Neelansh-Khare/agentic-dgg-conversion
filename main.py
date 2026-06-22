import os
from dotenv import load_dotenv
from src.agents.base_agents import OrchestrationAgent, PureMathAgent, DGGMLBridgeAgent
from src.memory.vector_memory import VectorMemory

load_dotenv()

def build_client():
    provider = os.getenv("LLM_PROVIDER", "zotgpt").lower()
    if provider == "ollama":
        from src.api.ollama_client import OllamaClient
        print(f"Using Ollama (model: {os.getenv('OLLAMA_MODEL', 'llama3')})")
        return OllamaClient()
    else:
        from src.api.zot_client import ZotGPTClient
        print("Using ZotGPT (Azure OpenAI)")
        return ZotGPTClient()

def main():
    print("Initializing DGG Multi-Agent System...")

    try:
        client = build_client()
        memory = VectorMemory()

        math_agent = PureMathAgent(client, memory, "PureMath", "pure_math")
        dggml_agent = DGGMLBridgeAgent(client, memory, "DGGMLBridge", "dggml_bridge")

        sub_agents = {"math": math_agent, "dggml": dggml_agent}
        orchestrator = OrchestrationAgent(client, memory, sub_agents)

        print("System ready for Phase 2: Knowledge Ingestion.")
        print("Next Steps:")
        print("1. Place research papers in 'base_documents/'")
        print("2. Run the ingestion script to populate the vector memory.")

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Initialization Failed: {e}")

if __name__ == "__main__":
    main()
