from abc import ABC, abstractmethod
from src.api.zot_client import ZotGPTClient
from src.memory.vector_memory import VectorMemory

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

    def run(self, user_input: str):
        context = self.retrieve_context(user_input)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context from Research:\n{context}\n\nTask: {user_input}"}
        ]
        return self.client.chat_completion(messages)

class PureMathAgent(BaseAgent):
    def _setup_system_prompt(self) -> str:
        return "You are the DGG Pure Math Agent. Use the provided context to formalize DGG rules in LaTeX."

class DGGMLBridgeAgent(BaseAgent):
    """
    Bridge to colleague's agent. 
    Passes the foundational math representation directly to the external agent,
    which is responsible for the final DGGML conversion.
    """
    def _setup_system_prompt(self) -> str:
        return (
            "You are the DGGML Interface. Your role is to take foundational "
            "mathematical representations of DGGs and prepare them for transmission "
            "to the specialized DGGML generation agent."
        )

    def call_colleague_agent(self, math_representation: str):
        """
        Sends the foundational math to the colleague's agent.
        Placeholder for real integration (API call or CLI execution).
        """
        print(f"[Bridge] Transmitting math representation to colleague's agent...")
        # Integration logic (e.g., requests.post) will go here.
        # For now, we simulate a successful handoff.
        return {
            "status": "transmitted",
            "payload_sent": math_representation,
            "message": "The external agent will now process this math into DGGML format."
        }

class OrchestrationAgent(BaseAgent):
    def __init__(self, client, memory, sub_agents):
        super().__init__(client, memory, "Orchestrator", "orchestration_agent")
        self.sub_agents = sub_agents

    def _setup_system_prompt(self) -> str:
        return "You are the Orchestrator. Decide which agent (PureMath or DGGML) to call based on the user request."

    def execute_pipeline(self, task: str):
        # 1. Orchestrator analyzes task
        decision = self.run(f"Determine the best workflow for: {task}")
        print(f"[Orchestrator] Plan: {decision['choices'][0]['message']['content']}")
        
        # 2. Logic to call sub_agents would go here (simplified for now)
        if "math" in task.lower():
            return self.sub_agents['math'].run(task)
        elif "dggml" in task.lower():
            math_out = self.sub_agents['math'].run(task)
            return self.sub_agents['dggml'].call_colleague_agent(math_out['choices'][0]['message']['content'])
