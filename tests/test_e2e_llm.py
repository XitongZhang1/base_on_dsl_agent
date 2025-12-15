import os
import asyncio
import logging
import pytest

from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import LLMIntentService, StubIntentService
from dsl_agent.ast_nodes import BinaryOpNode, FunctionCallNode


class DummyResp:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Msg", (), {"content": content})})()]


class DummyCompletions:
    def __init__(self, content: str):
        self._content = content

    def create(self, **_: object):
        return DummyResp(self._content)


class DummyChat:
    def __init__(self, content: str):
        self.completions = DummyCompletions(content)


class DummyClient:
    def __init__(self, content: str):
        self.chat = DummyChat(content)


class DummyClientFail:
    def __init__(self, exc: Exception):
        self._exc = exc
        self.chat = type("Chat", (), {"completions": type("C", (), {"create": self._raise})})()

    def _raise(self, **_):
        raise self._exc


def test_parse_script_preserves_ast_for_non_literal():
    path = "tests/test_data/dynamic_scenario.dsl"
    # Write scenario using a non-literal expression (string concat + intent())
    with open(path, "w", encoding="utf-8") as f:
        f.write('response start.ask_order: "Matched intent: " + intent(user_input)\nresponse start.default: "您好"')
    scen = parser.parse_script(path)
    st = scen.get_state("start")
    # the ask_order intent should exist
    assert "ask_order" in st.intents
    # the response for ask_order should be a BinaryOpNode (string + function call)
    resp = st.intents["ask_order"].response
    assert isinstance(resp, BinaryOpNode)
    # the right side should be a FunctionCallNode
    assert isinstance(resp.right, FunctionCallNode)


def test_e2e_with_mock_llm_client():
    path = "tests/test_data/dynamic_scenario.dsl"
    with open(path, "w", encoding="utf-8") as f:
        f.write('response start.ask_order: "Matched intent: " + intent(user_input)\nresponse start.default: "您好"')
    scen = parser.parse_script(path)

    # Dummy client returns 'ask_order'
    client = DummyClient("ask_order")
    svc = LLMIntentService(api_base="http://example", api_key="k", model="m", client=client)
    bot = Interpreter(scen, svc)
    reply = bot.process_input("我要查订单")
    assert "ask_order" in reply


def test_llm_api_failure_returns_none_and_logs(caplog):
    # arrange: scenario with ask_order and default
    path = "tests/test_data/dynamic_scenario.dsl"
    with open(path, "w", encoding="utf-8") as f:
        f.write('response start.ask_order: "Matched intent: " + intent(user_input)\nresponse start.default: "默认回复"')
    scen = parser.parse_script(path)
    # client that raises an error on call
    failing_client = DummyClientFail(RuntimeError("network"))
    svc = LLMIntentService(api_base="http://x", api_key="k", model="m", client=failing_client, max_retries=1)
    # ensure logs are captured
    caplog.set_level(logging.WARNING)
    # run identify - should return None and log a warning/error
    res = asyncio.run(svc.identify("hi", "start", ["ask_order"]))
    assert res is None
    assert any("LLM intent call failed" in rec.message for rec in caplog.records) or any("LLM intent call failed after retries" in rec.message for rec in caplog.records)


@pytest.mark.skipif(not os.environ.get("DSL_RUN_REAL_LLM"), reason="Run real LLM tests only when DSL_RUN_REAL_LLM env set")
def test_e2e_with_real_llm_if_enabled():
    # This test runs only when env var DSL_RUN_REAL_LLM is set.
    api_base = os.environ.get("DSL_API_BASE")
    api_key = os.environ.get("DSL_API_KEY")
    model = os.environ.get("DSL_MODEL")
    if not (api_base and api_key and model):
        pytest.skip("LLM env not configured")
    path = "tests/test_data/dynamic_scenario.dsl"
    with open(path, "w", encoding="utf-8") as f:
        f.write('response start.ask_order: "Matched intent: " + intent(user_input)\nresponse start.default: "您好"')
    scen = parser.parse_script(path)
    svc = LLMIntentService(api_base=api_base, api_key=api_key, model=model)
    bot = Interpreter(scen, svc)
    # expecting the real LLM to determine ask_order for the input below
    reply = bot.process_input("我要查订单")
    assert isinstance(reply, str)
