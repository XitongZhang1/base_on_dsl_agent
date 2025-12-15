import asyncio
from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import LLMIntentService


class DummyResp:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Msg", (), {"content": content})})()]


class PromptAwareDummyCompletions:
    def __init__(self, responder):
        self._responder = responder

    def create(self, **kwargs):
        messages = kwargs.get("messages", [])
        user_text = messages[-1]["content"] if messages else ""
        return DummyResp(self._responder(user_text))


class PromptAwareDummyClient:
    def __init__(self, responder):
        # client.chat.completions.create(...) expected by LLMIntentService
        self.chat = type("Chat", (), {"completions": PromptAwareDummyCompletions(responder)})()


def test_flight_booking_flow_with_llm_generate():
    scen = parser.parse_script("scenario/flight_booking.dsl")

    def responder(user_text: str):
        # if the prompt is for intent detection (it contains 'Allowed intents')
        if "Allowed intents" in user_text:
            return "provide_info"
        # if it's a generation prompt, return confirmation text
        if "Create a short booking confirmation" in user_text:
            return "Booking Confirmed: Flight ABC on 2025-01-01 from JFK to SFO"
        return "none"

    client = PromptAwareDummyClient(responder)
    svc = LLMIntentService(api_base="http://example", api_key="k", model="m", client=client)
    bot = Interpreter(scen, svc)

    r1 = bot.process_input("hello")
    assert "请输入" in r1 or "欢迎" in r1
    r2 = bot.process_input("info")
    assert "已收到信息" in r2
    r3 = bot.process_input("JFK to SFO on 2025-01-01")
    assert "Booking Confirmed" in r3
