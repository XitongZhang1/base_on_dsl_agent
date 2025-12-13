import asyncio

from dsl_agent.interpreter import Interpreter


class DummyTransition:
    def __init__(self, response, next_state=None):
        self.response = response
        self.next_state = next_state


class DummyState:
    def __init__(self, name, intents, default):
        self.name = name
        self.intents = intents
        self.default = default


class DummyScenario:
    def __init__(self, initial_state, states):
        self.initial_state = initial_state
        self._states = states

    def get_state(self, name):
        return self._states[name]


class FakeIntentService:
    def __init__(self, label):
        self.label = label

    async def identify(self, text: str, state: str, intents):
        return self.label


def test_process_input_sync_matches_intent():
    t = DummyTransition('ok {user_input}', next_state=None)
    s = DummyState('s1', {'check': t}, t)
    scenario = DummyScenario('s1', {'s1': s})
    svc = FakeIntentService('check')
    interp = Interpreter(scenario, svc)
    reply = interp.process_input('hello')
    assert 'hello' in reply
    assert interp.ended is True


def test_process_input_async_in_event_loop():
    t = DummyTransition('ok', next_state=None)
    s = DummyState('s1', {'a': t}, t)
    scenario = DummyScenario('s1', {'s1': s})
    svc = FakeIntentService('a')
    interp = Interpreter(scenario, svc)

    async def run():
        r = await interp.process_input_async('x')
        assert r == 'ok'

    asyncio.run(run())
