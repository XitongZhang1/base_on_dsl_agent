#!/usr/bin/env python3
"""Unified demo runner for scenario DSL files in demo and scenario directories.

Usage:
  python demo/run_demo.py --scenario banking_scenario
  python demo/run_demo.py --scenario flight_booking --use-real-llm

This utility loads the selected scenario, constructs the IntentService based on
CLI flags and `config.ini`, and runs an interactive REPL where each user input
is processed by the DSL interpreter.
"""
import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from dsl_agent import parser as dsl_parser
from dsl_agent import logic
from dsl_agent.interpreter import Interpreter


def build_bot_for_scenario(scenario: str, args) -> tuple[Interpreter, dict]:
    # Determine potential script paths: demo/<scenario>.dsl or scenario/<scenario>.dsl
    candidates = [Path('demo') / f"{scenario}.dsl", Path('scenario') / f"{scenario}.dsl", Path(scenario)]
    script_path = None
    for c in candidates:
        if c.exists():
            script_path = str(c)
            break
    if script_path is None:
        raise FileNotFoundError(f"Scenario file not found: searched {candidates}")

    cfg = logic._load_config(args.config) if args.config else {}
    settings = logic._resolve_settings(args, cfg)
    if args.use_stub is not None:
        settings['use_stub'] = args.use_stub
    if args.use_real_llm is not None:
        settings['use_real_llm'] = args.use_real_llm
    if args.api_base:
        settings['api_base'] = args.api_base
    if args.api_key:
        settings['api_key'] = args.api_key
    if args.model:
        settings['model'] = args.model

    svc = logic._build_intent_service(settings, scenario_name=scenario)
    scen = dsl_parser.parse_script(script_path)
    bot = Interpreter(scen, svc)
    return bot, settings


def main():
    p = argparse.ArgumentParser(description="Run demo scenario")
    p.add_argument('--scenario', '-s', required=True, help='Scenario to run (filename without .dsl or full path)')
    p.add_argument('--config', help='Optional path to config.ini')
    p.add_argument('--use-stub', dest='use_stub', action='store_true')
    p.add_argument('--no-stub', dest='use_stub', action='store_false')
    p.add_argument('--use-real-llm', dest='use_real_llm', action='store_true')
    p.add_argument('--api-base')
    p.add_argument('--api-key')
    p.add_argument('--model')
    p.add_argument('--provider')
    p.add_argument('--show-intent', dest='show_intent', action='store_true')
    p.add_argument('--log-file')
    p.add_argument('--idle-timeout', dest='idle_timeout', type=float)
    p.add_argument('--reset-each', dest='reset_each', action='store_true', help='Reset interpreter between inputs in the demo REPL')
    p.set_defaults(use_stub=None)
    args = p.parse_args()

    bot, settings = build_bot_for_scenario(args.scenario, args)
    print(f"Running scenario='{args.scenario}'. use_stub={settings.get('use_stub')}, use_real_llm={settings.get('use_real_llm')}")
    print("Type 'exit' to quit; empty input triggers default branch when idle timeout configured.")

    while True:
        try:
            user_text = input('> ')
        except EOFError:
            break
        if user_text.strip().lower() in {'exit', 'quit'}:
            break
        try:
            reply = bot.process_input(user_text)
        except Exception as exc:
            print('Error processing input:', exc)
            break
        print(reply)
        if args.reset_each:
            bot.reset()


if __name__ == '__main__':
    main()
