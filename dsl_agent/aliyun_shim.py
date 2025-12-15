"""Aliyun/OpenAI-compatible shim for LLM clients.

This module provides a lightweight wrapper with a `chat.completions.create`
interface that matches what the code expects from OpenAI-like SDKs.
It uses `requests` to call a provider endpoint and returns a simple object
with `.choices[0].message.content` similar to OpenAI responses.
"""
from __future__ import annotations

import json
import types
from typing import Any, Dict, Optional, Callable
import hmac
import hashlib
import base64
import datetime


class AliyunShim:
    def __init__(self, api_base: str, api_key: str, api_secret: Optional[str] = None, auth_header: Optional[str] = None, clock: Optional[Callable[[], str]] = None):
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self.chat = types.SimpleNamespace(completions=self)
        # allow custom header key, default to Authorization: Bearer <key>
        self._auth_header = auth_header or 'Authorization'
        # optional secret used to sign requests
        self._api_secret = api_secret
        # allow injecting a deterministic clock for unit tests
        self._clock = clock or (lambda: datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z')

    def create(self, model: str, messages: Any, max_tokens: int, temperature: float, timeout: float = 15.0):
        url = f"{self.api_base}/v1/chat/completions"
        try:
            import requests
        except Exception:
            raise RuntimeError("requests library required for AliyunShim but not installed")

        headers = {
            self._auth_header: f"Bearer {self.api_key}",
            'Content-Type': 'application/json',
        }
        # if api_secret provided, compute HMAC-SHA256 signature and include headers
        payload: Dict[str, Any] = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }
        # if api_secret provided, compute HMAC-SHA256 signature and include headers
        if self._api_secret:
            # canonicalize payload deterministically
            canonical_body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            timestamp = self._clock()
            canonical_str = f"POST\n/v1/chat/completions\n{timestamp}\n{canonical_body}"
            signature = base64.b64encode(hmac.new(self._api_secret.encode('utf-8'), canonical_str.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')
            # add signature header and access key header
            headers['X-Signature'] = signature
            headers['X-Access-Key'] = self.api_key
            headers['X-Timestamp'] = timestamp
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        resp = r.json()
        # normalize to have choices[0].message.content if not present
        try:
            content = resp['choices'][0]['message']['content']
        except Exception:
            # fallback to attempting text or returning full json
            try:
                content = resp['choices'][0]['text']
            except Exception:
                content = json.dumps(resp)
        message = types.SimpleNamespace(content=content)
        choice = types.SimpleNamespace(message=message)
        return types.SimpleNamespace(choices=[choice])
