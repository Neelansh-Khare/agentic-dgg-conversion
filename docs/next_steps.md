# Project Roadmap: Multi-Agent DGG Conversion System

This document outlines the specific technical steps required to complete the system, from knowledge ingestion to full multi-agent orchestration.

## Phase 2: Knowledge Ingestion & Retrieval (In Progress)
- [ ] **Data Gathering:** Populate `base_documents/` with DGG research papers (PDF/TXT).
- [ ] **Validation Run:** Execute `python -m src.utils.ingestion` and verify that `src/memory/vector_db` is populated.
- [ ] **RAG Integration:** Update `BaseAgent.run()` in `src/agents/base_agents.py` to automatically query `VectorMemory` and inject relevant context into the system prompt.

## Phase 3: Specialized Agent Implementation
- [ ] **Mathematica Agent:** 
    - Create `src/agents/mathematica_agent.py`.
    - Design prompts to handle Mathematica syntax (Rules, `GraphPlot`, `DifferentialEquations`).
- [ ] **DGGML Agent Integration:**
    - Coordinate with colleague to define the API/CLI handoff.
    - Implement a "Bridge Agent" in `src/agents/bridge_agent.py` that translates internal DGG Schema to DGGML.

## Phase 4: Communication & Orchestration
- [ ] **Inter-Agent Protocol:** Implement a message-passing system (e.g., LangGraph or a custom Dispatcher) so the Orchestrator can call sub-agents.
- [ ] **One-Shot Pipeline:** Create a "Conversion Pipeline" that:
    1. Orchestrator analyzes the input.
    2. Orchestrator delegates to the Pure Math agent for formalization.
    3. Results are passed to the Target Agent (Mathematica/DGGML).
    4. Orchestrator performs a final "Sanity Check" against DGG invariants.

## Phase 5: Testing & RL Feedback Loop
- [ ] **Automated Testing:** Populate `test_documents/` with known DGG examples.
- [ ] **Feedback Loop:** 
    - Implement a "Validation Tool" that attempts to parse generated DGGML or run generated Mathematica code.
    - If a syntax error occurs, feed the error back to the Orchestrator for a "retry" (RL-like behavior).
- [ ] **Performance Benchmarking:** Measure "one-shot" success rate vs. manual translation.

## Phase 6: Deployment & Finalization
- [ ] **CLI Interface:** Develop a robust CLI in `main.py` for easy user interaction.
- [ ] **Documentation:** Finalize API docs and user manuals.
