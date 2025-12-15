#!/usr/bin/env python3
"""Run flight booking demo using logic._build_intent_service to construct AliyunShim.
This script programmatically invokes the scenario with Aliyun provider.
"""
import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from dsl_agent import parser
from dsl_agent import logic
from dsl_agent.interpreter import Interpreter


def main():
    scen = parser.parse_script('scenario/flight_booking.dsl')
    cfg = logic._load_config(None)
    # Build a faux args object similar to CLI to pass provider from env
    class Args: pass
    args = Args()
    args.config = None
    args.use_stub = None
    args.use_real_llm = True
    args.api_base = os.getenv('DSL_API_BASE')
    args.api_key = os.getenv('DSL_API_KEY')
    args.model = os.getenv('DSL_MODEL')
    args.provider = os.getenv('DSL_PROVIDER')
    settings = logic._resolve_settings(args, cfg)
    svc = logic._build_intent_service(settings, scenario_name=scen.name)
    bot = Interpreter(scen, svc)

    inputs = ['查询', '北京到上海 2025-06-01']
    print('Initial state:', bot.current_state)
    for t in inputs:
        print('\nUser:', t)
        reply = bot.process_input(t)
        print('Bot:', reply)
        print('State:', bot.current_state)


if __name__ == '__main__':
    main()
