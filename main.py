import os
import json
import webbrowser
from dotenv import load_dotenv
from src.agents.base_agents import OrchestrationAgent, PureMathAgent, FoxflowAgent
from src.memory.vector_memory import VectorMemory
from src.utils.render import render_result_to_html

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
    print("=== DGG Agentic Conversion System PoC ===")

    try:
        client = build_client()
        memory = VectorMemory()

        math_agent = PureMathAgent(client, memory)
        foxflow_url = os.getenv("FOXFLOW_URL", "YOUR_NGROK_URL_HERE")
        foxflow_agent = FoxflowAgent(client, memory, api_url=foxflow_url)

        sub_agents = {"math": math_agent, "foxflow": foxflow_agent}
        orchestrator = OrchestrationAgent(client, memory, sub_agents)

        print("System ready. Sub-agents loaded: PureMath, Foxflow.")
        print("-" * 40)

        print("Tip: Ensure you have run 'python src/utils/ingestion.py' if you have new papers.")
        print("To use a test document, put it in 'tests/documents/' and reference its name.")
        user_query = input("Enter your conversion request: ")

        if not user_query:
            print("No query provided. Exiting.")
            return

        extra_context = ""
        if "tests/documents" in str(os.listdir("tests/documents")):
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
        renderable_text = None
        if isinstance(result, dict):
            if "llm_output" in result:
                print(f"LLM Representation:\n{result['llm_output']}")
                print(f"API Result: {result['api_result']}")
                renderable_text = result["llm_output"]
            elif "choices" in result:
                renderable_text = result["choices"][0]["message"]["content"]
                print(renderable_text)
            else:
                print(json.dumps(result, indent=2))
        else:
            print(result)
            renderable_text = str(result)

        if renderable_text:
            html_path = render_result_to_html(renderable_text)
            print(f"[System] Rendered view: {html_path}")
            webbrowser.open(html_path.resolve().as_uri())

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
