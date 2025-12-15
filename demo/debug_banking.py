#!/usr/bin/env python3
"""Interactive demo for banking scenario.

Usage:
  python demo/debug_banking.py [--config config.ini] [--use-stub] [--use-real-llm] [--api-base BASE --api-key KEY --model MODEL]

This demo uses `dsl_agent.logic` helper routines to resolve settings and build the IntentService.
"""
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from dsl_agent import parser
from dsl_agent import logic
from dsl_agent.interpreter import Interpreter


def build_bot(args):
	cfg = logic._load_config(args.config) if args.config else {}
	settings = logic._resolve_settings(args, cfg)
	# build intent service using existing helper
	svc = logic._build_intent_service(settings, scenario_name='banking_scenario')
	scen = parser.parse_script('scenario/banking_scenario.dsl')
	return Interpreter(scen, svc), settings


def main():
	p = argparse.ArgumentParser()
	p.add_argument('--config', help='path to config.ini')
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
	p.add_argument('--reset-each', dest='reset_each', action='store_true', help='Reset interpreter between inputs')
	p.set_defaults(use_stub=None)
	args = p.parse_args()

	bot, settings = build_bot(args)

	print(f"[banking] interactive. use_stub={settings.get('use_stub')}, use_real_llm={settings.get('use_real_llm')}")
	print("Type 'exit' to quit. Try: '查询余额', then 'api_response'")
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
