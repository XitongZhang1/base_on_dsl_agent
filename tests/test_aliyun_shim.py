import json
import types
from pathlib import Path
import pytest

from dsl_agent.aliyun_shim import AliyunShim


class DummyResp:
    def __init__(self, content):
        self._content = content

    def json(self):
        return {
            'choices': [{'message': {'content': self._content}}]
        }


class DummyRequests:
    def __init__(self, content):
        self.content = content

    def post(self, url, json, headers, timeout):
        return types.SimpleNamespace(status_code=200, json=lambda: {'choices': [{'message': {'content': self.content}}]})


def test_aliyun_shim_calls(monkeypatch):
    expected = 'hello from aliyun shim'
    # Inject a dummy requests module into sys.modules to avoid needing the requests package
    import sys
    class FakeRequests:
        def post(self, url, json, headers, timeout):
            return types.SimpleNamespace(status_code=200, json=lambda: {'choices': [{'message': {'content': expected}}]}, raise_for_status=lambda: None)
    sys.modules['requests'] = FakeRequests()
    shim = AliyunShim(api_base='https://fake', api_key='key')
    res = shim.create(model='m', messages=[{'role': 'user', 'content': 'hi'}], max_tokens=10, temperature=0.0, timeout=5.0)
    assert res.choices[0].message.content == expected


def test_logic_builds_client_with_provider(monkeypatch):
    # Build settings as logic would produce and import the shim class to validate
    from dsl_agent.logic import _build_intent_service
    settings = {
        'api_base': 'https://fake',
        'api_key': 'key',
        'api_secret': 'secret',
        'model': 'm',
        'provider': 'aliyun',
        'use_stub': False,
        'use_real_llm': False,
    }
    # monkeypatch AliyunShim to avoid network
    class MockShim:
        def __init__(self, api_base, api_key, api_secret=None, **kwargs):
            self.api_base = api_base
            self.api_key = api_key
            self.api_secret = api_secret

        def create(self, *args, **kwargs):
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='ok'))])

    # monkeypatch the actual module where AliyunShim is defined
    monkeypatch.setattr('dsl_agent.aliyun_shim.AliyunShim', MockShim)
    svc = _build_intent_service(settings, scenario_name='whatever')
    # should be LLMIntentService and have client attribute pointing to MockShim
    from dsl_agent.LLM_integration import LLMIntentService
    assert isinstance(svc, LLMIntentService)
    assert isinstance(svc.client, MockShim)
    assert getattr(svc.client, 'api_secret', None) == 'secret'


def test_aliyun_shim_signature_header(monkeypatch):
    # ensure expected signature header is computed and sent
    expected_content = 'hello signed'
    api_base = 'https://fake'
    api_key = 'mykey'
    api_secret = 'mysecret'
    timestamp = '2025-12-14T12:00:00Z'

    # fake requests to capture headers
    import sys
    captured = {}
    class FakeRequestsForSign:
        def post(self, url, json, headers, timeout):
            captured['url'] = url
            captured['json'] = json
            captured['headers'] = headers
            return types.SimpleNamespace(status_code=200, json=lambda: {'choices': [{'message': {'content': expected_content}}]}, raise_for_status=lambda: None)
    sys.modules['requests'] = FakeRequestsForSign()

    # deterministic clock
    from dsl_agent.aliyun_shim import AliyunShim
    shim = AliyunShim(api_base=api_base, api_key=api_key, api_secret=api_secret, clock=lambda: timestamp)
    res = shim.create(model='m', messages=[{'role': 'user', 'content': 'hi'}], max_tokens=10, temperature=0.0, timeout=5.0)
    assert res.choices[0].message.content == expected_content
    headers = captured.get('headers', {})
    # verify presence of expected headers
    assert headers.get('X-Access-Key') == api_key
    assert headers.get('X-Timestamp') == timestamp
    assert 'X-Signature' in headers
    # compute expected signature the same way AliyunShim does
    canonical_body = json.dumps(captured['json'], separators=(',', ':'), sort_keys=True)
    canonical_str = f"POST\n/v1/chat/completions\n{timestamp}\n{canonical_body}"
    import hmac, hashlib, base64
    expected_sig = base64.b64encode(hmac.new(api_secret.encode('utf-8'), canonical_str.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')
    assert headers['X-Signature'] == expected_sig
