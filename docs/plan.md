# Project Plan: Multi-Agent Dynamical Graph Grammar (DGG) Conversion System

## 1. Executive Summary
This project aims to develop a multi-agent system capable of "one-shot" conversion between various representations of Dynamical Graph Grammars (DGGs). The system will bridge the gap between pure mathematical descriptions, domain-specific languages (DGGML), and computational environments (Mathematica).

## 2. Core Objectives
- **One-Shot Conversion:** Achieve high-fidelity translations between representations in a single execution flow.
- **Deep Domain Expertise:** Leverage a specialized "Orchestration Agent" with exhaustive knowledge of DGG theory that will conserve semantic meaning of DGGs
- **Interoperability:** Seamlessly integrate with external agents (e.g., the existing DGGML agent).
- **Academic Rigor:** Utilize the UCI Zot API (Azure OpenAI) and base the system's intelligence on peer-reviewed research papers.

## 3. System Architecture

### A. Orchestration Agent (The "Brain")
- **Role:** Master controller and domain expert.
- **Function:** Decomposes conversion requests, identifies source/target nuances, and validates the output against DGG mathematical invariants.
- **Knowledge Base:** Initialized with core DGG research papers (Mjolness et al.).

### B. Specialized Agents
- **Pure Math Agent:** Handles LaTeX-style mathematical definitions, graph rewrite rules, and differential equation mappings.
- **DGGML Agent:** (Colleague-integrated) Manages the DGG Markup Language representation.
- **Mathematica Agent:** Converts DGG logic into executable Mathematica code/notebooks.

## 4. Agent Persistence & Knowledge Integration
To avoid "starting from scratch" on every call, we will implement agent persistence through the following layers:

### Layer 1: Persistent Vector Memory (RAG)
- **Mechanism:** Research papers are indexed in a vector database (e.g., Pinecone, Chroma, or FAISS).
- **Benefit:** Agents can retrieve specific mathematical proofs or syntax rules without consuming the entire context window.

### Layer 2: Domain-Specific Fine-Tuning (The "RL" Aspect)
- **RL Exploration:** If accuracy plateaus, we will implement Reinforcement Learning from Compiler Feedback (RLCF). The Mathematica or DGGML agent attempts to "run" the conversion; if it fails, the error is fed back to the Orchestrator to "learn" the correction.
- **Fine-tuning:** Periodic fine-tuning of models using the Zot API on corrected datasets to bake DGG syntax directly into the model weights.

### Layer 3: Agent Identity & State Management
To achieve true persistence beyond stateless API calls:
- **Persistent System Prompts:** Each agent will have a "Persona Profile" that evolves as it "learns" from the research papers.
- **Session Caching:** Implement a caching layer for common mathematical transformations to ensure consistency across conversions.
- **Long-term Memory:** Use a graph-based memory (e.g., Knowledge Graph) to store relationships between DGG concepts discovered during research ingestion, allowing agents to "remember" previous reasoning paths.

## 5. Integration Strategy (UCI Zot API)
The system will interface with the UCI Zot API using the Azure OpenAI schema.
- **Endpoint:** `https://azureapi.zotgpt.uci.edu/openai/deployments/{deployment-id}/chat/completions`
- **Security:** API keys and deployment IDs will be managed via environment variables.
- **Colleague's Agent:** We will define a standardized JSON-RPC or REST interface to hand off tasks to the existing DGGML agent, ensuring the Orchestrator can treat it as a "tool" or "sub-agent".

## 6. Implementation Roadmap

### Phase 1: Foundation (Current Focus)
- Setup project infrastructure.
- Implement the **Orchestration Agent** and **Pure Math Agent**.
- Develop a shared "DGG Schema" to act as an intermediate representation (IR) between agents.

### Phase 2: Knowledge Ingestion
- Batch process foundational papers using the Zot API embeddings endpoint.
- Populating the vector memory with DGG concepts.

### Phase 3: Integration
- Establish communication with the colleague's DGGML agent.
- Implement the **Mathematica Agent**.

### Phase 4: Optimization & RL
- Implement the feedback loop for self-correction.
- Evaluate one-shot performance against known DGG benchmarks.

## 7. Alternatives Considered
- **UCI Zot API vs. Public OpenAI:** Zot API is preferred for academic compliance and data privacy at UCI. If rate limits become an issue, we may consider local Llama-3/Mistral instances for preprocessing tasks.
- **Zero-shot vs. Few-shot:** While the goal is one-shot, we will use a "Chain of Thought" (CoT) prompting strategy internally between agents to ensure correctness before presenting the final one-shot output to the user.
