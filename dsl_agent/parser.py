# parser.py
import re
from typing import List, Tuple, Optional
from .ast_nodes import *

class DSLParser:
    """简单的DSL解析器（支持基础语法）"""
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
    
    def parse(self, script: str) -> List[ASTNode]:
        """解析DSL脚本为AST节点列表"""
        lines = script.strip().split('\n')
        statements = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 解析不同类型的语句
            if line.startswith('response '):
                statements.append(self._parse_response(line))
            elif '=' in line and not line.startswith('if') and not line.startswith('while'):
                statements.append(self._parse_assignment(line))
            elif line.startswith('if '):
                # 暂时不支持多行 if 块；标记为未实现以便未来扩展
                raise SyntaxError('Block statements (if/while) are not supported in this simplified parser')
        
        return statements
    
    def _parse_response(self, line: str) -> ResponseNode:
        """解析响应语句: response greeting: "Hello" """
        match = re.match(r'response\s+([^:]+):\s+(.+)', line)
        if not match:
            raise SyntaxError(f"Invalid response statement: {line}")
        
        response_type = match.group(1)
        content_str = match.group(2).strip()
        
        # 解析内容表达式
        content_expr = self._parse_expression(content_str)
        
        return ResponseNode(response_type, content_expr)
    
    def _parse_assignment(self, line: str) -> AssignmentNode:
        """解析赋值语句: x = 10 + 5 """
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise SyntaxError(f"Invalid assignment: {line}")
        
        var_name = parts[0].strip()
        expr_str = parts[1].strip()
        
        # 解析右侧表达式
        value_expr = self._parse_expression(expr_str)
        
        return AssignmentNode(var_name, value_expr)
    
    def _parse_expression(self, expr_str: str) -> ASTNode:
        """解析表达式"""
        expr_str = expr_str.strip()
        # 字符串字面量，支持单/双引号与基本转义
        if (expr_str.startswith('"') and expr_str.endswith('"')) or (
            expr_str.startswith("'") and expr_str.endswith("'")
        ):
            inner = expr_str[1:-1]
            inner = inner.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
            return StringNode(inner)

        # 数字字面量（支持整数、浮点、负数、科学计数法）
        if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", expr_str):
            return NumberNode(float(expr_str))

        # 布尔字面量
        if expr_str.lower() in ('true', 'false'):
            return BoolNode(expr_str.lower() == 'true')

        # 函数调用（支持空参数列表与简单的嵌套逗号分割）
        if re.match(r"^\w+\(.*\)$", expr_str):
            return self._parse_function_call(expr_str)

        # 变量名
        if re.match(r'^[A-Za-z_]\w*$', expr_str):
            return VariableNode(expr_str)

        # 二元运算：在最外层(括号深度为0)查找最低优先级运算符
        ops_precedence = [r'\bor\b', r'\band\b', '==', '!=', '>=', '<=', '>', '<', '\+', '-', '\*', '/']
        for op in ops_precedence:
            pos = self._find_top_level_operator(expr_str, op)
            if pos != -1:
                left = expr_str[:pos].strip()
                op_str = expr_str[pos:pos + len(re.findall(op, expr_str[:pos+1]) and op or op)]
                # For word ops like 'and'/'or' extract by regex match
                if op.startswith('\\b'):
                    # regex find at top-level
                    m = re.search(op, expr_str)
                    if m:
                        left = expr_str[:m.start()].strip()
                        right = expr_str[m.end():].strip()
                        operator = m.group(0)
                    else:
                        continue
                else:
                    # symbol operator
                    operator = expr_str[pos]
                    right = expr_str[pos + 1:].strip()
                return BinaryOpNode(operator.strip(), self._parse_expression(left), self._parse_expression(right))

        # 默认回退为字符串字面量（保留原行为，但不吞掉明显的语法错误）
        return StringNode(expr_str)
    
    def _parse_function_call(self, expr_str: str) -> FunctionCallNode:
        """解析函数调用: func(arg1, arg2) """
        match = re.match(r"^(\w+)\((.*)\)$", expr_str)
        if not match:
            raise SyntaxError(f"Invalid function call: {expr_str}")

        func_name = match.group(1)
        args_str = match.group(2)

        # 解析参数，按逗号分割但尊重括号嵌套
        args = []
        if args_str.strip():
            parts = []
            depth = 0
            start = 0
            for i, ch in enumerate(args_str):
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                elif ch == ',' and depth == 0:
                    parts.append(args_str[start:i].strip())
                    start = i + 1
            parts.append(args_str[start:].strip())
            for part in parts:
                if part:
                    args.append(self._parse_expression(part))

        return FunctionCallNode(func_name, args)

    def _find_top_level_operator(self, s: str, op_pattern: str) -> int:
        """在字符串 s 中查找 top-level（不在括号内）的运算符位置，返回第一个匹配的起始索引或 -1。"""
        depth = 0
        if op_pattern.startswith('\\b'):
            # word operator handled separately by regex over full string
            for m in re.finditer(op_pattern, s):
                # ensure match is at top-level by checking parentheses before match.start()
                prefix = s[:m.start()]
                for ch in prefix:
                    if ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                if depth == 0:
                    return m.start()
            return -1

        # symbol operator
        # op_pattern is a literal like '+' or '==' etc.; we search characters
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif depth == 0:
                # try to match multi-char ops at this position
                for op in ['==', '!=', '>=', '<=', '+', '-', '*', '/', '>', '<']:
                    if s.startswith(op, i):
                        return i
            i += 1
        return -1


# Lightweight scenario model for compatibility with Interpreter and CLI
class Transition:
    def __init__(self, response, next_state: Optional[str] = None):
        # response may be a plain string or an ASTNode (to be executed at runtime)
        self.response = response
        self.next_state = next_state


class State:
    def __init__(self, name: str, intents: Optional[Dict[str, Transition]] = None, default: Optional[Transition] = None):
        self.name = name
        self.intents = intents or {}
        self.default = default or Transition("")


class Scenario:
    def __init__(self, name: str, initial_state: str, states: Dict[str, State]):
        self.name = name
        self.initial_state = initial_state
        self._states = states

    def get_state(self, name: str) -> State:
        return self._states[name]


def parse_script(path) -> Scenario:
    """Read a simplified DSL file and return a lightweight Scenario.

    The simplified DSL is expected to contain `response <type>: "..."` lines.
    This helper maps the first response as the state's default reply and
    exposes other response types as possible named responses (not used as intents).
    """
    from pathlib import Path
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    parser = DSLParser()
    nodes = parser.parse(text)

    # derive scenario name
    name = p.stem

    # build states and intents. support response types like "state.intent"
    states: Dict[str, State] = {}
    first_state: Optional[str] = None

    try:
        from .ast_nodes import ResponseNode, StringNode
    except Exception:
        ResponseNode = None
        StringNode = None

    for node in nodes:
        if ResponseNode and isinstance(node, ResponseNode):
            resp_type = getattr(node, 'response_type', 'default')
            content_node = getattr(node, 'content', None)
            # Keep the AST node (do not eagerly execute at parse time) so the
            # interpreter can evaluate it with a runtime context (e.g. llm client).
            if content_node is None:
                txt = StringNode("")
            else:
                # Keep literal string values as plain strings for backward
                # compatibility with tests and simple templating replacement.
                if StringNode and isinstance(content_node, StringNode):
                    txt = content_node.value
                else:
                    txt = content_node

            # support optional next state: state.intent->nextstate
            next_state = None
            if '->' in resp_type:
                left, next_state = resp_type.split('->', 1)
                resp_type = left
                # record reference to possibly forward-declared state
                if next_state:
                    referenced_next_states = referenced_next_states if 'referenced_next_states' in locals() else set()
                    referenced_next_states.add(next_state)

            # split state.intent if provided
            if '.' in resp_type:
                st, intent = resp_type.split('.', 1)
            else:
                st, intent = name, resp_type

            if first_state is None:
                first_state = st

            if st not in states:
                states[st] = State(st, intents={}, default=Transition(''))

            states[st].intents[intent] = Transition(txt, next_state=next_state)
            # if state has no default yet, set this as default
            if not states[st].default.response:
                states[st].default = Transition(txt, next_state=next_state)

    initial = 'start' if 'start' in states else (first_state or name)
    # ensure any referenced next-states exist as placeholder states
    if 'referenced_next_states' in locals():
        for ns in referenced_next_states:
            if ns not in states:
                states[ns] = State(ns, intents={}, default=Transition(''))
    scen = Scenario(name=name, initial_state=initial, states=states)
    return scen