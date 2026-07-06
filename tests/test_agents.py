import json

import pytest

from src.agents.base_agents import FoxflowAgent, OrchestrationAgent, PureMathAgent
from tests.conftest import FakeClient, FakeMemory


def test_retrieve_context_filters_by_agent_scope():
    memory = FakeMemory(documents=["doc a", "doc b"])
    agent = PureMathAgent(FakeClient(), memory)

    context = agent.retrieve_context("some query")

    assert context == "doc a\ndoc b"
    assert memory.queries[0]["where"] == {"agent_scope": {"$in": ["pure_math", "general_knowledge"]}}


def test_run_appends_extra_context_when_provided():
    client = FakeClient()
    agent = PureMathAgent(client, FakeMemory(documents=["base context"]))

    agent.run("convert this", extra_context="transient pdf text")

    user_message = client.calls[0][1]["content"]
    assert "base context" in user_message
    assert "[Transient Test Context]:\ntransient pdf text" in user_message


def test_run_omits_transient_marker_without_extra_context():
    client = FakeClient()
    agent = PureMathAgent(client, FakeMemory(documents=["base context"]))

    agent.run("convert this")

    user_message = client.calls[0][1]["content"]
    assert "[Transient Test Context]" not in user_message


def test_foxflow_call_api_without_configured_url_skips_network_call(mocker):
    post = mocker.patch("src.agents.base_agents.requests.post")
    agent = FoxflowAgent(FakeClient(), FakeMemory())

    result = agent.call_foxflow_api({"description": "x"})

    assert result == {"error": "API URL not configured"}
    post.assert_not_called()


def test_foxflow_call_api_returns_error_dict_on_request_failure(mocker):
    mocker.patch("src.agents.base_agents.requests.post", side_effect=ConnectionError("refused"))
    agent = FoxflowAgent(FakeClient(), FakeMemory(), api_url="http://example.test")

    result = agent.call_foxflow_api({"description": "x"})

    assert result == {"error": "refused"}


def test_foxflow_run_combines_llm_output_with_api_result(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok"}
    mocker.patch("src.agents.base_agents.requests.post", return_value=mock_response)

    client = FakeClient({"choices": [{"message": {"content": "foxflow json here"}}]})
    agent = FoxflowAgent(client, FakeMemory(), api_url="http://example.test")

    result = agent.run("build a predator/prey model")

    assert result == {"llm_output": "foxflow json here", "api_result": {"status": "ok"}}


def _orchestrator(decision_content, math_client=None, foxflow_client=None):
    orchestrator_client = FakeClient({"choices": [{"message": {"content": decision_content}}]})
    memory = FakeMemory()
    sub_agents = {
        "math": PureMathAgent(math_client or FakeClient({"choices": [{"message": {"content": "math result"}}]}), memory),
        "foxflow": FoxflowAgent(foxflow_client or FakeClient({"choices": [{"message": {"content": "foxflow result"}}]}), memory),
    }
    return OrchestrationAgent(orchestrator_client, memory, sub_agents)


def test_execute_pipeline_routes_to_math_agent_on_clean_json():
    decision = json.dumps({"target": "math", "reasoning": "user wants LaTeX", "concepts": ["diffusion"]})
    orchestrator = _orchestrator(decision)

    result = orchestrator.execute_pipeline("formalize the diffusion rule")

    assert result["choices"][0]["message"]["content"] == "math result"


def test_execute_pipeline_strips_markdown_json_fence():
    decision = "```json\n" + json.dumps({"target": "foxflow", "reasoning": "r", "concepts": []}) + "\n```"
    orchestrator = _orchestrator(decision)

    result = orchestrator.execute_pipeline("convert to foxflow")

    assert result["llm_output"] == "foxflow result"


def test_execute_pipeline_falls_back_to_math_keyword_on_unparsable_decision():
    orchestrator = _orchestrator("not valid json at all")

    result = orchestrator.execute_pipeline("please do some MATH for me")

    assert result["choices"][0]["message"]["content"] == "math result"


def test_execute_pipeline_falls_back_to_foxflow_when_no_math_keyword():
    orchestrator = _orchestrator("not valid json at all")

    result = orchestrator.execute_pipeline("please convert this description")

    assert result["llm_output"] == "foxflow result"
