import asyncio

from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import StubIntentService


def test_dynamic_response_includes_intent_label():
    # create a minimal DSL that uses runtime intent() in the response
    text = 'response start.ask_order: "Matched intent: " + intent(user_input)\nresponse start.default: "您好"'
    # write a temp file under tests/test_data
    p = 'tests/test_data/dynamic_scenario.dsl'
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)

    scenario = parser.parse_script(p)
    # stub: in 'start' state, if text contains '我要查订单' return 'ask_order'
    mapping = {'start': {'我要查订单': 'ask_order'}}
    svc = StubIntentService(mapping=mapping)
    bot = Interpreter(scenario, svc)

    reply = bot.process_input('我要查订单')
    assert 'ask_order' in reply
