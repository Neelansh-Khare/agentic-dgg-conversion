from abc import ABC, abstractmethod
from src.api.zot_client import ZotGPTClient
from src.memory.vector_memory import VectorMemory
import requests
import json

class BaseAgent(ABC):
    def __init__(self, client: ZotGPTClient, memory: VectorMemory, name: str, scope: str):
        self.client = client
        self.memory = memory
        self.name = name
        self.scope = scope
        self.system_prompt = self._setup_system_prompt()

    @abstractmethod
    def _setup_system_prompt(self) -> str:
        pass

    def retrieve_context(self, query: str, n=3):
        """Retrieves context filtered by the agent's specific scope."""
        results = self.memory.collection.query(
            query_texts=[query],
            n_results=n,
            where={"agent_scope": {"$in": [self.scope, "general_knowledge"]}}
        )
        return "\n".join(results['documents'][0]) if results['documents'] else ""

    def run(self, user_input: str, extra_context: str = ""):
        context = self.retrieve_context(user_input)
        combined_context = f"{context}\n\n[Transient Test Context]:\n{extra_context}" if extra_context else context
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context from Research:\n{combined_context}\n\nTask: {user_input}"}
        ]
        return self.client.chat_completion(messages)

class PureMathAgent(BaseAgent):
    def __init__(self, client, memory):
        super().__init__(client, memory, "PureMath", "pure_math")

    def _setup_system_prompt(self) -> str:
        return (
            "You are the DGG Pure Math Agent. Your expertise is in Dynamical Graph Grammars (DGGs) "
            "as defined by Mjolness et al. Use the provided context to formalize DGG rules into "
            "LaTeX mathematical notation, focusing on graph rewrite rules and associated differential equations.\n\n"
            "In addition to the LaTeX formalization, always include a Graphviz DOT diagram of the graph "
            "rewrite rule (its 'before' and 'after' subgraphs), fenced as a ```dot code block, e.g.:\n"
            "```dot\n"
            "digraph rule {\n"
            "  rankdir=LR;\n"
            "  subgraph cluster_before { label=\"before\"; u; v; u -> v [label=\"w_uv\"]; }\n"
            "  subgraph cluster_after { label=\"after\"; u2 [label=\"u\"]; v2 [label=\"v\"]; x [label=\"x'\"]; "
            "u2 -> v2; v2 -> x; }\n"
            "}\n"
            "```\n"
            "Every double-quoted label must be closed on the same line it opens. Avoid raw apostrophes "
            "inside quoted labels (e.g. for x-prime, write x_prime or xp rather than x' or x''), since an "
            "unescaped quote character inside a label breaks the DOT parser. Node names must be plain "
            "identifiers (letters, digits, underscores only) with no apostrophes or bare LaTeX in them "
            "(write u_prime, not u'). Every label value must be plain quoted text, not raw LaTeX commands "
            "or $...$ math delimiters — the LaTeX belongs only in the prose/formula section above, "
            "never inside the ```dot block."
        )

class FoxflowAgent(BaseAgent):
    """
    Agent that connects to an external Foxflow service via API.
    """
    def __init__(self, client, memory, api_url="YOUR_NGROK_URL_HERE"):
        super().__init__(client, memory, "Foxflow", "foxflow")
        self.api_url = api_url

    def _setup_system_prompt(self) -> str:
        return (
            "You are the Foxflow Agent. Your role is to convert DGG descriptions into the "
            "specific JSON-based format required by the Foxflow engine. Use the provided context "
            "to ensure the mapping is semantically correct."
        )

    def call_foxflow_api(self, data: dict):
        """Sends data to the Foxflow ngrok endpoint."""
        if self.api_url == "YOUR_NGROK_URL_HERE":
            print("[Foxflow] Warning: API URL not configured.")
            return {"error": "API URL not configured"}
        
        try:
            response = requests.post(f"{self.api_url}/convert", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Foxflow] API Call Failed: {e}")
            return {"error": str(e)}

    def run(self, user_input: str, extra_context: str = ""):
        # First, generate the intermediate representation using LLM
        context = self.retrieve_context(user_input)
        combined_context = f"{context}\n\n[Transient Test Context]:\n{extra_context}" if extra_context else context
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context:\n{combined_context}\n\nTask: Prepare Foxflow representation for: {user_input}"}
        ]
        llm_response = self.client.chat_completion(messages)
        representation = llm_response['choices'][0]['message']['content']
        
        # Then, optionally send it to the API
        print(f"[Foxflow] Generated representation. Sending to API...")
        api_result = self.call_foxflow_api({"description": representation})
        return {
            "llm_output": representation,
            "api_result": api_result
        }

class OrchestrationAgent(BaseAgent):
    def __init__(self, client, memory, sub_agents):
        super().__init__(client, memory, "Orchestrator", "general_knowledge")
        self.sub_agents = sub_agents

    def _setup_system_prompt(self) -> str:
        return (
            "You are the DGG Orchestrator. You receive requests to convert DGG concepts from research papers "
            "into specific formats. Your job is to:\n"
            "1. Analyze the user request.\n"
            "2. Determine if the target is 'Math' (LaTeX) or 'Foxflow' (Computational).\n"
            "3. Extract relevant DGG names or concepts from the request to guide sub-agents.\n"
            "Respond ONLY with a JSON object: {\"target\": \"math\" | \"foxflow\", \"reasoning\": \"...\", \"concepts\": [...]}"
        )

    def execute_pipeline(self, task: str, extra_context: str = ""):
        print(f"[Orchestrator] Analyzing task: {task}")
        
        # 1. Decision making
        raw_decision = self.run(task, extra_context=extra_context)
        try:
            # Try to parse JSON from the LLM response
            content = raw_decision['choices'][0]['message']['content']
            # Basic cleaning in case LLM adds markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            decision = json.loads(content)
            print(f"[Orchestrator] Target: {decision['target'].upper()}")
        except Exception as e:
            print(f"[Orchestrator] Error parsing decision: {e}. Defaulting based on keywords.")
            if "math" in task.lower():
                decision = {"target": "math"}
            else:
                decision = {"target": "foxflow"}

        # 2. Routing
        if decision['target'] == "math":
            print("[Orchestrator] Routing to PureMath Agent...")
            return self.sub_agents['math'].run(task, extra_context=extra_context)
        elif decision['target'] == "foxflow":
            print("[Orchestrator] Routing to Foxflow Agent...")
            return self.sub_agents['foxflow'].run(task, extra_context=extra_context)
        else:
            return "Unknown target."
