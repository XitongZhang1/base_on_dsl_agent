from dsl_agent.LLM_integration import LLMIntentService


def test_normalize_result_matches_lowercase_intent():
    svc = LLMIntentService(api_base='', api_key='', model='')
    # simulate LLM returned content
    out = svc._normalize_result('CHECK_BALANCE', ['check_balance', 'other'])
    assert out == 'check_balance'


def test_normalize_result_none():
    svc = LLMIntentService(api_base='', api_key='', model='')
    assert svc._normalize_result('none', ['a', 'b']) is None
