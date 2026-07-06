import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class FakeClient:
    """Stand-in for ZotGPTClient/OllamaClient. Queue responses or set a fixed one."""

    def __init__(self, response=None):
        self._response = response or {"choices": [{"message": {"content": "default response"}}]}
        self.calls = []

    def chat_completion(self, messages, temperature=0.7, max_tokens=1024):
        self.calls.append(messages)
        return self._response


class FakeMemory:
    """Stand-in for VectorMemory. Records the `where` filter used on each query."""

    def __init__(self, documents=None):
        self._documents = documents if documents is not None else ["retrieved context"]
        self.queries = []

        class _Collection:
            def query(collection_self, query_texts, n_results, where=None):
                self.queries.append({"query_texts": query_texts, "n_results": n_results, "where": where})
                return {"documents": [self._documents]}

        self.collection = _Collection()
