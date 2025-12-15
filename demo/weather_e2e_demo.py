#!/usr/bin/env python3
"""Demonstration: use a dummy LLM client to perform intent classification
on weather scenario and drive interpreter execution.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

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
        # Our LLM integration expects the content to be 'intent' label or 'none'
        return DummyResp(self._responder(user_text))


class PromptAwareDummyClient:
    def __init__(self, responder):
        self.chat = type("Chat", (), {"completions": PromptAwareDummyCompletions(responder)})()


def responder(user_text: str) -> str:
    # Determine the user's original phrase inside the LLM prompt
    # The LLM prompt includes 'User said: "<text>"', so we search for common keywords
    txt = user_text.lower()
    if any(k in txt for k in ["预报", "未来", "明天"]):
        return "forecast_help"
    if any(k in txt for k in ["空气", "aqi", "污染"]):
        return "aqi_help"
    if any(k in txt for k in ["预警", "警报", "灾害"]):
        return "warning_help"
    # default to current weather
    return "current_weather_help"


def main():
    scen = parser.parse_script('scenario/weather_scenario.dsl')
    client = PromptAwareDummyClient(responder)
    svc = LLMIntentService(api_base='http://example', api_key='k', model='m', client=client)
    bot = Interpreter(scen, svc)

    tests = [
        '请给我上海未来三天天气',
        '北京的空气质量如何',
        '广州今天的天气',
        '有没有台风预警',
    ]
    for t in tests:
        print('User:', t)
        print('Bot:', bot.process_input(t))
        # Reset interpreter between tests so each is treated as a new conversation
        bot.reset()
        print('---')


if __name__ == '__main__':
    main()
