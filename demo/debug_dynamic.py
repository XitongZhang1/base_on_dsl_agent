#!/usr/bin/env python3
"""Interactive demo for dynamic AST execution with intent() and llm_generate() support.

Usage:
  python demo/debug_dynamic.py [--config config.ini] [--use-stub] [--use-real-llm]
"""
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from dsl_agent import parser
from dsl_agent import logic
from dsl_agent.interpreter import Interpreter
import asyncio


DEFAULT_P = 'tests/test_data/dynamic_scenario.dsl'
DEFAULT_SCRIPT = 'response start.ask_order: "Matched intent: " + intent(user_input)\nresponse start.default: "您好"'


def build_bot(script_path, args):
    # ensure the script exists
    if script_path == DEFAULT_P:
        Path(script_path).parent.mkdir(parents=True, exist_ok=True)
        Path(script_path).write_text(DEFAULT_SCRIPT, encoding='utf-8')
    scen = parser.parse_script(script_path)
    cfg = logic._load_config(args.config) if args.config else {}
    settings = logic._resolve_settings(args, cfg)
    svc = logic._build_intent_service(settings, scenario_name=scen.name)
    return Interpreter(scen, svc), scen, settings


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--script', default=DEFAULT_P)
    p.add_argument('--config')
    p.add_argument('--api-base')
    p.add_argument('--api-key')
    p.add_argument('--model')
    p.add_argument('--provider')
    p.add_argument('--use-stub', dest='use_stub', action='store_true')
    p.add_argument('--no-stub', dest='use_stub', action='store_false')
    p.add_argument('--use-real-llm', dest='use_real_llm', action='store_true')
    p.add_argument('--show-intent', dest='show_intent', action='store_true')
    p.add_argument('--log-file')
    p.add_argument('--idle-timeout', dest='idle_timeout', type=float)
    p.add_argument('--reset-each', dest='reset_each', action='store_true', help='Reset interpreter between inputs')
    p.set_defaults(use_stub=None)
    args = p.parse_args()

    bot, scen, settings = build_bot(args.script, args)
    print(f"Scenario {scen.name} loaded. use_stub={settings.get('use_stub')}, use_real_llm={settings.get('use_real_llm')}")
    print("Type 'exit' to quit. Try: '我要查订单' or 'anything' to see default path.")
    while True:
        try:
            text = input('> ')
        except EOFError:
            break
        if text.strip().lower() in ('exit', 'quit'):
            break
        reply = bot.process_input(text)
        print(reply)
        if args.reset_each:
            bot.reset()


if __name__ == '__main__':
    main()
