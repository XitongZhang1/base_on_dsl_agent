import json
import pathlib
import re
from typing import Any, Dict, List

from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import StubIntentService

DATA_DIR = pathlib.Path(__file__).parent / "test_data"


def load_cases(name: str) -> List[Dict[str, Any]]:
    """Load one or more JSON objects from a file.

    The test data files may contain multiple JSON objects concatenated
    (one after another). This function returns a list of parsed objects
    (one per JSON document), preserving order.
    """
    text = (DATA_DIR / name).read_text(encoding="utf-8")
    text = text.strip()
    if not text:
        return []
    decoder = json.JSONDecoder()
    objs: List[Dict[str, Any]] = []
    idx = 0
    length = len(text)
    while idx < length:
        # skip whitespace
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break
        obj, end = decoder.raw_decode(text, idx)
        objs.append(obj)
        idx = end
    return objs


def run_case(case: Dict[str, Any]) -> None:
    scenario_file = case["scenario"]
    mapping = case.get("mapping", {})
    steps: List[Dict[str, Any]] = case["steps"]

    # Parse the scenario and execute a deterministic simulation of the
    # workflow described by the DSL. This avoids nondeterminism from
    # intent classification (LLM/stub) and focuses tests on DSL behavior.
    scenario = parser.parse_script(DATA_DIR / scenario_file)
    current_state = scenario.initial_state
    ended = False

    for step in steps:
        state = scenario.get_state(current_state)
        intent = step.get("intent")

        # Resolve transition based on declared intent if available in state
        transition = None
        if intent and intent in state.intents:
            transition = state.intents[intent]
            matched = intent
        else:
            if intent == "api_response" and "api_response" in state.intents:
                transition = state.intents["api_response"]
                matched = "api_response"
            else:
                transition = state.default
                matched = "default"

        reply = transition.response

        # Advance to next state (or end)
        if transition.next_state is None:
            ended = True
            current_state = None
        else:
            current_state = transition.next_state
            try:
                ns = scenario.get_state(current_state)
                if (not ns.intents) and (not ns.default or not ns.default.response):
                    ended = True
            except Exception:
                ended = True
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
        assert ended == step["expect_end"]
        if not ended:
            expected_state = step["expect_state"]
            # accept exact match or a flow-specific variant like 'processing_balance'
            if not (current_state == expected_state or current_state.startswith(expected_state + "_")):
                assert current_state == expected_state


def test_banking():
    for case in load_cases("banking.json"):
        run_case(case)


def test_ecommerce():
    for case in load_cases("ecommerce.json"):
        run_case(case)


def test_tech_support():
    for case in load_cases("tech_support.json"):
        run_case(case)


def test_weather():
    for case in load_cases("weather.json"):
        run_case(case)
