import asyncio
from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import LLMIntentService


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


def test_llm_generate_with_dummy_client():
    path = "tests/test_data/llm_generate_scenario.dsl"
    with open(path, "w", encoding="utf-8") as f:
        f.write('response start.default: llm_generate("X:" + user_input)')
    scen = parser.parse_script(path)
    client = DummyClient("generated: answer")
    svc = LLMIntentService(api_base="http://example", api_key="k", model="m", client=client)
    bot = Interpreter(scen, svc)
    reply = bot.process_input("hello")
    assert "generated: answer" in reply


def test_llm_generate_demo_scenario():
    path = "scenario/llm_generate_demo.dsl"
    scen = parser.parse_script(path)
    client = DummyClient("Hello from LLM")
    svc = LLMIntentService(api_base="http://example", api_key="k", model="m", client=client)
    bot = Interpreter(scen, svc)
    reply = bot.process_input("world")
    assert "Hello from LLM" in reply
