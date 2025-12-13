import json
import pathlib
import re
from typing import Any, Dict, List

from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import StubIntentService

DATA_DIR = pathlib.Path(__file__).parent / "test_data"


def load_case(name: str) -> Dict[str, Any]:
    # Accept files that may contain multiple concatenated JSON objects
    text = (DATA_DIR / name).read_text(encoding="utf-8").strip()
    if not text:
        return {}
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    return obj


def run_case(case: Dict[str, Any]) -> None:
    scenario_file = case["scenario"]
    mapping = case.get("mapping", {})
    steps: List[Dict[str, Any]] = case["steps"]

    scenario = parser.parse_script(DATA_DIR / scenario_file)
    stub = StubIntentService(mapping=mapping)
    bot = Interpreter(scenario, stub)

    for step in steps:
        reply = bot.process_input(step["user"])
        expected = step["expect_reply"]
        # treat patterns containing regex-like tokens as regex
        try:
            if re.search(expected, reply):
                matched = True
            else:
                matched = False
        except re.error:
            matched = expected in reply
        assert matched, f"Expected pattern {expected!r} in reply {reply!r}"
        assert bot.ended == step["expect_end"]
        if not bot.ended:
            assert bot.current_state == step["expect_state"]


def test_banking():
    run_case(load_case("banking.json"))


def test_ecommerce():
    run_case(load_case("ecommerce.json"))


def test_tech_support():
    run_case(load_case("tech_support.json"))


def test_weather():
    run_case(load_case("weather.json"))
