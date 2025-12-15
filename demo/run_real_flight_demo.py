#!/usr/bin/env python3
"""Programmatically run a scenario with real LLM and print outputs.
This avoids interactive stdin issues and captures replies programmatically.
"""
import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import LLMIntentService


def main():
    scen = parser.parse_script('scenario/flight_booking.dsl')
    api_base = os.getenv('DSL_API_BASE')
    api_key = os.getenv('DSL_API_KEY')
    model = os.getenv('DSL_MODEL')
    provider = os.getenv('DSL_PROVIDER', 'openai')
    if not (api_base and api_key and model):
        print('Missing API credentials; set DSL_API_BASE, DSL_API_KEY, DSL_MODEL')
        return
    svc = LLMIntentService(api_base=api_base, api_key=api_key, model=model)
    bot = Interpreter(scen, svc)
    inputs = [
        '查询',
        '北京到上海 2025-06-01',
    ]
    print('Initial state:', bot.current_state)
    for t in inputs:
        print('\nUser:', t)
        reply = bot.process_input(t)
        print('Bot:', reply)
        print('State:', bot.current_state, 'Ended:', bot.ended)


if __name__ == '__main__':
    main()
