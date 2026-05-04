import os
import sys
from src.api.zot_client import ZotGPTClient
from src.agents.base_agents import OrchestrationAgent, PureMathAgent
from src.memory.vector_memory import VectorMemory

def main():
    print("Initializing DGG Multi-Agent System...")
    
    try:
        # Initialize Client
        client = ZotGPTClient()
        
        # Initialize Memory
        memory = VectorMemory()
        
        # Initialize Agents
        orchestrator = OrchestrationAgent(client, "Orchestrator")
        math_agent = PureMathAgent(client, "PureMath")
        
        print("System ready for Phase 2: Knowledge Ingestion.")
        print("Next Steps:")
        print("1. Place research papers in 'base_documents/'")
        print("2. Run the ingestion script (to be developed) to populate the vector memory.")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Initialization Failed: {e}")

if __name__ == "__main__":
    main()
