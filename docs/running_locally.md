# Running the pipeline locally (no API key)

The system defaults to ZotGPT (Azure OpenAI), which needs `ZOTGPT_API_KEY`. To
run without any key, switch to Ollama and point at a locally pulled model.

## PowerShell

```powershell
$env:LLM_PROVIDER = "ollama"
$env:OLLAMA_MODEL = "llama3.2"
$env:OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
.venv\Scripts\python.exe main.py
```

## Git Bash

```bash
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=llama3.2
export OLLAMA_EMBEDDING_MODEL=nomic-embed-text
.venv/Scripts/python.exe main.py
```

Then at the `Enter your conversion request:` prompt, type e.g.:

```
formalize the diffusion rule for math
```

Requires Ollama running locally (`http://localhost:11434` by default) with
the model and embedding model already pulled:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Known issue

The orchestrator's routing decision expects clean JSON back from the LLM.
`llama3.2` tends to append prose after the JSON blob, so `json.loads` throws
and every real (non-mocked) request currently falls back to the keyword
heuristic in `execute_pipeline` (`"math" in task.lower()` vs. Foxflow). It
still lands on the right agent by luck of wording, not the intended
LLM-routing path — worth tightening before wiring more sub-agents through
the same orchestrator.
