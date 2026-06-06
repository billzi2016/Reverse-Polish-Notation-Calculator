import pytest
from src.core.parser import parse
from src.ast_tree.nodes import NumberNode, OperatorNode, FunctionNode


class TestASTStructureBasic:
    def test_single_number(self):
        ast = parse("42")
        assert isinstance(ast, NumberNode)
        assert ast.value == 42.0

    def test_simple_add(self):
        ast = parse("3 + 4")
        assert isinstance(ast, OperatorNode)
        assert ast.symbol == "+"
        assert isinstance(ast.left,  NumberNode) and ast.left.value  == 3.0
        assert isinstance(ast.right, NumberNode) and ast.right.value == 4.0

    def test_simple_multiply(self):
        ast = parse("2 * 5")
        assert isinstance(ast, OperatorNode) and ast.symbol == "*"

    def test_precedence_mul_over_add(self):
        # 3 + 4 * 2  →  +(3, *(4,2))
        ast = parse("3 + 4 * 2")
        assert isinstance(ast, OperatorNode) and ast.symbol == "+"
        assert isinstance(ast.right, OperatorNode) and ast.right.symbol == "*"

    def test_precedence_parens_override(self):
        # (3 + 4) * 2  →  *(+(3,4), 2)
        ast = parse("(3 + 4) * 2")
        assert isinstance(ast, OperatorNode) and ast.symbol == "*"
        assert isinstance(ast.left, OperatorNode) and ast.left.symbol == "+"


class TestAssociativity:
    def test_left_assoc_subtraction(self):
        # 5 - 3 - 1  →  -(-(5,3), 1)
        ast = parse("5 - 3 - 1")
        assert isinstance(ast, OperatorNode) and ast.symbol == "-"
        assert isinstance(ast.left, OperatorNode) and ast.left.symbol == "-"

    def test_right_assoc_power(self):
        # 2 ^ 3 ^ 2  →  ^(2, ^(3,2))
        ast = parse("2 ^ 3 ^ 2")
        assert isinstance(ast, OperatorNode) and ast.symbol == "^"
        assert isinstance(ast.right, OperatorNode) and ast.right.symbol == "^"


class TestFunctionNode:
    def test_sin_zero(self):
        ast = parse("sin(0)")
        assert isinstance(ast, FunctionNode)
        assert ast.name == "sin"
        assert isinstance(ast.argument, NumberNode) and ast.argument.value == 0.0

    def test_all_functions_parse(self):
        for fn in ["sin", "cos", "tan", "log"]:
            ast = parse(f"{fn}(1)")
            assert isinstance(ast, FunctionNode) and ast.name == fn

    def test_nested_function_expr(self):
        # sin(3 + 4)
        ast = parse("sin(3 + 4)")
        assert isinstance(ast, FunctionNode) and ast.name == "sin"
        assert isinstance(ast.argument, OperatorNode)

    def test_function_in_expr(self):
        # sin(3 + 4) * 2  →  *(sin(...), 2)
        ast = parse("sin(3 + 4) * 2")
        assert isinstance(ast, OperatorNode) and ast.symbol == "*"
        assert isinstance(ast.left, FunctionNode)


class TestErrors:
    def test_unmatched_left_paren(self):
        with pytest.raises(ValueError):
            parse("(3 + 4")

    def test_unmatched_right_paren(self):
        with pytest.raises(ValueError):
            parse("3 + 4)")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse("")

    def test_double_operator_raises(self):
        with pytest.raises(ValueError):
            parse("3 + + 4")
