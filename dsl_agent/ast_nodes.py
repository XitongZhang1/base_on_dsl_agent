# ast_nodes.py
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Union
from dataclasses import dataclass
import json

class ASTNode(ABC):
    """抽象语法树节点基类"""
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        pass

    async def execute_async(self, context: Dict[str, Any]) -> Any:
        # Default implementation delegates to sync execute for nodes
        # that do not require async work.
        return self.execute(context)
    
    @abstractmethod
    def __repr__(self) -> str:
        pass

@dataclass
class NumberNode(ASTNode):
    value: float
    
    def execute(self, context: Dict[str, Any]) -> float:
        return self.value
    
    def __repr__(self) -> str:
        return str(self.value)

@dataclass
class StringNode(ASTNode):
    value: str
    
    def execute(self, context: Dict[str, Any]) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f'"{self.value}"'

@dataclass
class BoolNode(ASTNode):
    value: bool
    
    def execute(self, context: Dict[str, Any]) -> bool:
        return self.value
    
    def __repr__(self) -> str:
        return "true" if self.value else "false"

@dataclass
class VariableNode(ASTNode):
    name: str
    
    def execute(self, context: Dict[str, Any]) -> Any:
        if self.name in context:
            return context[self.name]
        raise NameError(f"Undefined variable: {self.name}")
    
    def __repr__(self) -> str:
        return self.name

@dataclass
class BinaryOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode
    
    def execute(self, context: Dict[str, Any]) -> Any:
        left_val = self.left.execute(context)
        right_val = self.right.execute(context)
        
        # 支持的操作符
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else 0,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            'and': lambda a, b: bool(a) and bool(b),
            'or': lambda a, b: bool(a) or bool(b),
        }
        
        if self.op in ops:
            return ops[self.op](left_val, right_val)
        raise ValueError(f"Unknown operator: {self.op}")
    
    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"

    async def execute_async(self, context: Dict[str, Any]) -> Any:
        left_val = await self.left.execute_async(context)
        right_val = await self.right.execute_async(context)
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else 0,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            'and': lambda a, b: bool(a) and bool(b),
            'or': lambda a, b: bool(a) or bool(b),
        }
        if self.op in ops:
            return ops[self.op](left_val, right_val)
        raise ValueError(f"Unknown operator: {self.op}")

@dataclass
class AssignmentNode(ASTNode):
    var_name: str
    value_expr: ASTNode
    
    def execute(self, context: Dict[str, Any]) -> Any:
        value = self.value_expr.execute(context)
        context[self.var_name] = value
        return value
    
    def __repr__(self) -> str:
        return f"{self.var_name} = {self.value_expr}"

    async def execute_async(self, context: Dict[str, Any]) -> Any:
        value = await self.value_expr.execute_async(context)
        context[self.var_name] = value
        return value

@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None
    
    def execute(self, context: Dict[str, Any]) -> Any:
        cond_result = self.condition.execute(context)
        
        if bool(cond_result):
            for stmt in self.then_block:
                result = stmt.execute(context)
        elif self.else_block:
            for stmt in self.else_block:
                result = stmt.execute(context)
        
        return None
    
    def __repr__(self) -> str:
        result = f"if {self.condition} {{\n"
        for stmt in self.then_block:
            result += f"  {stmt};\n"
        result += "}"
        if self.else_block:
            result += " else {\n"
            for stmt in self.else_block:
                result += f"  {stmt};\n"
            result += "}"
        return result

    async def execute_async(self, context: Dict[str, Any]) -> Any:
        cond_result = await self.condition.execute_async(context)
        if bool(cond_result):
            for stmt in self.then_block:
                await stmt.execute_async(context)
        elif self.else_block:
            for stmt in self.else_block:
                await stmt.execute_async(context)
        return None

@dataclass
class ResponseNode(ASTNode):
    """响应节点 - 核心客服功能"""
    response_type: str  # greeting, info, question, transfer, etc.
    content: ASTNode
    metadata: Optional[Dict] = None
    
    def execute(self, context: Dict[str, Any]) -> Any:
        content_value = self.content.execute(context)
        
        # 触发响应回调
        if "response_callback" in context:
            callback = context["response_callback"]
            callback(self.response_type, content_value, self.metadata)
        
        # 存储到上下文
        context["last_response"] = {
            "type": self.response_type,
            "content": content_value,
            "metadata": self.metadata
        }
        
        return content_value
    
    def __repr__(self) -> str:
        return f"response {self.response_type}: {self.content}"

    async def execute_async(self, context: Dict[str, Any]) -> Any:
        content_value = await self.content.execute_async(context)
        if "response_callback" in context:
            callback = context["response_callback"]
            callback(self.response_type, content_value, self.metadata)
        context["last_response"] = {
            "type": self.response_type,
            "content": content_value,
            "metadata": self.metadata,
        }
        return content_value

@dataclass
class FunctionCallNode(ASTNode):
    func_name: str
    args: List[ASTNode]
    
    def execute(self, context: Dict[str, Any]) -> Any:
        # 内置函数
        builtins = {
            "print": lambda args: print(*args),
            "len": lambda args: len(args[0]) if args else 0,
            "intent": lambda args: self._call_intent_api(args, context),
            "json_parse": lambda args: json.loads(args[0]) if args else {},
        }
        
        # 执行参数
        arg_values = [arg.execute(context) for arg in self.args]
        
        if self.func_name in builtins:
            return builtins[self.func_name](arg_values)
        elif "functions" in context and self.func_name in context["functions"]:
            return context["functions"][self.func_name](*arg_values)
        
        raise NameError(f"Undefined function: {self.func_name}")
    
    def _call_intent_api(self, args, context):
        """调用LLM进行意图识别"""
        if "llm_client" in context:
            user_input = args[0] if args else ""
            return context["llm_client"].get_intent(user_input)
        return "unknown"
    
    def __repr__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.func_name}({args_str})"

    async def execute_async(self, context: Dict[str, Any]) -> Any:
        import asyncio as _asyncio

        arg_values = [await arg.execute_async(context) for arg in self.args]
        # Async-capable builtins
        async def _intent_async(args_list):
            user_input = args_list[0] if args_list else ""
            service = context.get("intent_service") or context.get("llm_client")
            if service is None:
                return "unknown"
            # Prefer coroutine identify if present
            try:
                ident = service.identify
            except Exception:
                ident = None
            if hasattr(ident, "__call__"):
                # If identify is coroutine function
                if _asyncio.iscoroutinefunction(ident):
                    # Use default state and intents if provided in context
                    state_name = context.get("state_name")
                    intents = context.get("state_intents", [])
                    return await ident(user_input, state_name, intents)
                else:
                    # sync identify
                    return ident(user_input, context.get("state_name"), context.get("state_intents", []))
            # legacy: if provided llm_client has get_intent callable
            get_intent = context.get("llm_client", {}).get("get_intent") if isinstance(context.get("llm_client"), dict) else None
            if callable(get_intent):
                return get_intent(user_input)
            return "unknown"

        async def _llm_generate_async(args_list):
            # args_list[0] is the prompt
            prompt = args_list[0] if args_list else ""
            service = context.get("llm_client") or context.get("intent_service")
            if service is None:
                return ""
            # Prefer coroutine generate if present
            gen = getattr(service, "generate", None)
            if gen is None:
                # fallback to None
                return ""
            if _asyncio.iscoroutinefunction(gen):
                return await gen(prompt)
            # if it's sync, call it in thread
            return await _asyncio.to_thread(gen, prompt)

        async def _json_parse(args_list):
            import json as _json
            try:
                return _json.loads(args_list[0]) if args_list else {}
            except Exception:
                return {}

        async def _len_async(args_list):
            return len(args_list[0]) if args_list else 0

        # map async builtins
        builtins_async = {
            "intent": _intent_async,
            "json_parse": _json_parse,
            "len": _len_async,
            "llm_generate": _llm_generate_async,
        }

        # map sync builtins
        builtins_sync = {
            "print": lambda args_list: print(*args_list),
        }

        if self.func_name in builtins_async:
            return await builtins_async[self.func_name](arg_values)
        if self.func_name in builtins_sync:
            return builtins_sync[self.func_name](arg_values)
        elif "functions" in context and self.func_name in context["functions"]:
            func = context["functions"][self.func_name]
            if _asyncio.iscoroutinefunction(func):
                return await func(*arg_values)
            return func(*arg_values)

        raise NameError(f"Undefined function: {self.func_name}")