import os
import sys
import json
from src.api.zot_client import ZotGPTClient
from src.agents.base_agents import OrchestrationAgent, PureMathAgent, FoxflowAgent
from src.memory.vector_memory import VectorMemory

def main():
    print("=== DGG Agentic Conversion System PoC ===")
    
    try:
        # Initialize Client
        client = ZotGPTClient()
        
        # Initialize Memory
        memory = VectorMemory()
        
        # Initialize Specialized Agents
        math_agent = PureMathAgent(client, memory)
        # The Foxflow URL can be set via environment variable or edited below
        foxflow_url = os.getenv("FOXFLOW_URL", "YOUR_NGROK_URL_HERE")
        foxflow_agent = FoxflowAgent(client, memory, api_url=foxflow_url)
        
        # Initialize Orchestrator with sub-agents
        sub_agents = {
            "math": math_agent,
            "foxflow": foxflow_agent
        }
        orchestrator = OrchestrationAgent(client, memory, sub_agents)
        
        print("System ready. Sub-agents loaded: PureMath, Foxflow.")
        print("-" * 40)
        
        # Example Workflow
        print("Tip: Ensure you have run 'python src/utils/ingestion.py' if you have new papers.")
        print("To use a test document, put it in 'tests/documents/' and reference its name.")
        user_query = input("Enter your conversion request: ")
        
        if not user_query:
            print("No query provided. Exiting.")
            return

        # Check for local test document content to provide as 'extra context'
        extra_context = ""
        if "tests/documents" in str(os.listdir("tests/documents")): # Check if dir is not empty
             # Simple heuristic: if user mentions a filename in tests/documents
             for root, dirs, files in os.walk("tests/documents"):
                 for f in files:
                     if f.lower() in user_query.lower() and (f.endswith(".txt") or f.endswith(".pdf")):
                         print(f"[System] Found test document: {f}. Reading content...")
                         file_path = os.path.join(root, f)
                         if f.endswith(".txt"):
                             with open(file_path, "r") as tf:
                                 extra_context = tf.read()
                         elif f.endswith(".pdf"):
                             from pypdf import PdfReader
                             reader = PdfReader(file_path)
                             for page in reader.pages:
                                 extra_context += page.extract_text() + "\n"
                         break

        result = orchestrator.execute_pipeline(user_query, extra_context=extra_context)
        
        print("-" * 40)
        print("FINAL OUTPUT:")
        if isinstance(result, dict):
            if "llm_output" in result: # From FoxflowAgent
                print(f"LLM Representation:\n{result['llm_output']}")
                print(f"API Result: {result['api_result']}")
            elif "choices" in result: # Standard LLM response
                print(result['choices'][0]['message']['content'])
            else:
                print(json.dumps(result, indent=2))
        else:
            print(result)
            
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
