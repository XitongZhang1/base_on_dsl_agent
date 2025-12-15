#!/usr/bin/env python3
"""Test runner for Aliyun flight demo — injects a fake `requests` module to
capture headers and avoid making real network calls. Prints captured headers
for verification and runs the demo script.
"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

# set fake environment values
os.environ['DSL_API_BASE'] = 'https://fake'
os.environ['DSL_API_KEY'] = 'mykey'
os.environ['DSL_API_SECRET'] = 'mysecret'
os.environ['DSL_MODEL'] = 'm'
os.environ['DSL_PROVIDER'] = 'aliyun'

captured = {}
class FakeRequests:
    def post(self, url, json, headers, timeout):
        captured['url'] = url
        captured['json'] = json
        captured['headers'] = headers
        return type('R', (), {'status_code':200, 'json': lambda *a, **k: {'choices':[{'message':{'content':'ok'}}]}, 'raise_for_status': lambda *a, **k: None})()

sys.modules['requests'] = FakeRequests()

# run the demo main() function
from dsl_agent import parser
from dsl_agent import logic
from dsl_agent.interpreter import Interpreter

def run_demo():
    scen = parser.parse_script('scenario/flight_booking.dsl')
    cfg = logic._load_config(None)
    class Args: pass
    args = Args()
    args.config = None
    args.use_stub = None
    args.use_real_llm = True
    args.api_base = os.getenv('DSL_API_BASE')
    args.api_key = os.getenv('DSL_API_KEY')
    args.model = os.getenv('DSL_MODEL')
    args.provider = os.getenv('DSL_PROVIDER')
    args.show_intent = None
    args.log_file = None
    args.idle_timeout = None
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

try:
    run_demo()
finally:
    print('\nCaptured headers:')
    for k, v in captured.get('headers', {}).items():
        print(f"{k}: {v}")
