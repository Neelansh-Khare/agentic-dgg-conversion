# Experiment 1: DGG to Math/Foxflow Conversion

This experiment demonstrates a "one-shot" conversion of Dynamical Graph Grammars (DGGs) from research papers into two target formats: LaTeX Math and Foxflow JSON.

## Prerequisites
- [ ] UCI ZotGPT API Key (set in `.env`)
- [ ] Foxflow API running and exposed via ngrok
- [ ] Python virtual environment active (`source venv/bin/activate`)

## Setup Steps

### 1. Ingest Base Knowledge
Place foundational papers (e.g., Mjolness et al.) that the agents should "know" into `base_documents/general_knowledge/`.
```bash
python src/utils/ingestion.py
```

### 2. Configure Foxflow
Update `main.py` or set the `FOXFLOW_URL` environment variable with your ngrok endpoint.

### 3. Run the Conversion
Run the main script and provide a prompt referencing a specific DGG rule.
```bash
python main.py
```

## Testing "New" Papers
If you have a paper you want to test **without** indexing it into the long-term memory (RAG):
1. Place it in the `tests/documents/` folder.
2. In your prompt, provide the specific text or snippet from that paper.
3. The Orchestrator will use the **General Knowledge** from memory to interpret the **New Snippet** you provide in the prompt.

## Expected Results
- **Math Target:** A LaTeX block containing rewrite rules and ODEs.
- **Foxflow Target:** A JSON payload sent to the API and a confirmation response.
