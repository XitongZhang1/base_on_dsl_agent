#!/usr/bin/env python3
# Demo: run flight_booking scenario with stubbed intent and generation
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from dsl_agent import parser
from dsl_agent import LLM_integration
from dsl_agent.interpreter import Interpreter

scen = parser.parse_script('scenario/flight_booking.dsl')

class TestStub(LLM_integration.StubIntentService):
    async def identify(self, text, state, intents):
        if '查询' in text:
            return 'provide_info'
        if '订票' in text or '票' in text:
            return 'provide_info'
        return None

    async def generate(self, prompt, max_tokens=None, temperature=None):
        return f"Stubbed LLM generation: {prompt}"

svc = TestStub()
bot = Interpreter(scen, svc)

print('User: (initial)')
print('Bot:', bot.process_input('hello'))
print('Bot state:', bot.current_state)

print('\nUser: 查询')
print('Bot:', bot.process_input('查询'))
print('Bot state:', bot.current_state)

print('\nUser: 北京到上海 2025-06-01')
print('Bot:', bot.process_input('北京到上海 2025-06-01'))
