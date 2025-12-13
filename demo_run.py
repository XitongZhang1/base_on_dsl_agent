from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import StubIntentService

# use the simplified test scenario used in tests
scenario = parser.parse_script("tests/test_data/banking_scenario.dsl")
# mapping: when in 'start' state, input '查询余额' -> intent '查询余额'
stub = StubIntentService(mapping={"start": {"查询余额": "查询余额"}, "processing": {"api_response": "api_response"}})
bot = Interpreter(scenario, stub)

print("User: 查询余额")
print("Bot:", bot.process_input("查询余额"))
# simulate user waiting/empty input to trigger default/API response
print("User: api_response")
print("Bot:", bot.process_input("api_response"))
