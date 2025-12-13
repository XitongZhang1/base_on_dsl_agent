from dsl_agent import parser
from dsl_agent.interpreter import Interpreter
from dsl_agent.LLM_integration import StubIntentService

# Use the simplified test scenario for banking
scenario = parser.parse_script("tests/test_data/banking_scenario.dsl")
# stub mapping: map user utterances to intents per state
mapping = {
    "start": {"查询余额": "查询余额", "转账": "转账"},
    "processing": {"api_response": "api_response"},
}
stub = StubIntentService(mapping=mapping)
bot = Interpreter(scenario, stub)

# Simulated interactive sequence
steps = [
    ("查询余额", True),
    ("(等待)", False),  # show a user pause; we'll instead send the api_response intent
    ("api_response", True),
]

print(f"--- Simulated interactive demo for scenario: {scenario.name} ---\n")
for user_text, show_user_flag in steps:
    if show_user_flag:
        print("User:", user_text)
        out = bot.process_input(user_text)
        print("Bot:", out)
    else:
        # simulate a pause/default trigger by calling the intent that the system expects
        print("User: (no input / timeout)")
        out = bot.process_input("api_response")
        print("Bot:", out)
    if bot.ended:
        print("[Conversation ended]")
        break

print('\n--- Demo finished ---')
