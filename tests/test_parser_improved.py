from dsl_agent.parser import DSLParser
from dsl_agent.ast_nodes import StringNode, NumberNode, FunctionCallNode, BinaryOpNode


def test_string_escape_and_quotes():
    p = DSLParser()
    node = p._parse_expression('"hello \\\"world\\\""')
    assert isinstance(node, StringNode)
    assert node.value == 'hello \"world\"'


def test_number_parsing():
    p = DSLParser()
    n = p._parse_expression('3.14')
    assert isinstance(n, NumberNode)
    assert abs(n.value - 3.14) < 1e-9


def test_function_empty_and_nested_args():
    p = DSLParser()
    f = p._parse_expression('fn()')
    assert isinstance(f, FunctionCallNode)
    assert f.func_name == 'fn'
    assert f.args == []

    g = p._parse_expression('f(a, g(x,y), 3)')
    assert isinstance(g, FunctionCallNode)
    assert g.func_name == 'f'
    assert len(g.args) == 3
    assert isinstance(g.args[1], FunctionCallNode)


def test_binary_ops_without_spaces():
    p = DSLParser()
    b = p._parse_expression('1+2*3')
    assert isinstance(b, BinaryOpNode)
    # top-level '+' expected, right side is '2*3'
    assert b.op == '+'
    assert isinstance(b.right, BinaryOpNode)
