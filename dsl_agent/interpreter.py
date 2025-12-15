from __future__ import annotations

import asyncio
import inspect
import logging
from typing import List, Optional, Any

from .LLM_integration import IntentService
from .ast_nodes import ASTNode

logger = logging.getLogger(__name__)


class Interpreter:
    def __init__(self, scenario: Scenario, intent_service: IntentService):
        self.scenario = scenario
        self.intent_service = intent_service
        self._current_state = scenario.initial_state
        self._ended = False

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def ended(self) -> bool:
        return self._ended

    def reset(self) -> None:
        self._current_state = self.scenario.initial_state
        self._ended = False

    def process_input(self, user_text: str) -> str:
        # 提供同步入口，但在已有事件循环中不可调用
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None
        if running_loop is not None and running_loop.is_running():
            raise RuntimeError("process_input cannot be called from a running event loop; use process_input_async")
        return asyncio.run(self.process_input_async(user_text))

    async def process_input_async(self, user_text: str) -> str:
        if self._ended:
            raise RuntimeError("Conversation already ended")

        state = self.scenario.get_state(self._current_state)
        available_intents: List[str] = list(state.intents.keys())

        # 调用意图服务（awaitable）
        intent = await self.intent_service.identify(user_text, state.name, available_intents)

        # 统一意图 key 为小写以便匹配
        mapping = {k.lower(): v for k, v in state.intents.items()}

        if intent is not None:
            normalized = intent.strip().lower()
        else:
            normalized = None

        if normalized and normalized in mapping:
            transition = mapping[normalized]
            matched = normalized
        else:
            transition = state.default
            matched = "default"

        # Prepare runtime context for AST execution
        context = {
            "intent_service": self.intent_service,
            "llm_client": self.intent_service,
            "state_name": state.name,
            "state_intents": available_intents,
            "user_input": user_text,
            "variables": {},
            "functions": {},
            # response_callback can be used by ResponseNode to report breadcrumbs
            "response_callback": None,
        }

        # If the transition response is an ASTNode, execute it with the async API.
        if isinstance(transition.response, ASTNode):
            try:
                reply_val = await transition.response.execute_async(context)
                reply = str(reply_val)
            except Exception:
                # fallback to empty reply on execution error
                reply = ""
        else:
            # Plain string -> use legacy behavior
            reply = transition.response.replace("{user_input}", user_text)

        if transition.next_state is None:
            self._ended = True
            next_state = None
        else:
            next_state = transition.next_state
            self._current_state = next_state

        # If we entered a state that has no intents and no default response, treat it as terminal.
        if next_state is not None:
            try:
                new_state = self.scenario.get_state(next_state)
                if (not new_state.intents) and (not new_state.default or not new_state.default.response):
                    self._ended = True
            except Exception:
                # if the next state cannot be resolved, consider conversation ended
                self._ended = True

        logger.info(
            "state=%s intent=%s next=%s ended=%s",
            state.name,
            matched,
            next_state if next_state is not None else "end",
            self._ended,
        )
        return reply

    def _resolve_intent(self, user_text: str, state: str, intents: List[str]) -> Optional[str]:
        # 旧接口兼容：保留同步调用路径（尽可能不使用）
        result = self.intent_service.identify(user_text, state, intents)
        if inspect.isawaitable(result):
            result = asyncio.run(result)
        if result is None:
            return None
        normalized = result.strip().lower()
        if not normalized:
            return None
        return normalized