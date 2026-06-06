import pytest
from src.core.rpn_converter import infix_to_rpn


class TestBasicConversion:
    def test_simple_add(self):
        assert infix_to_rpn("3 + 4") == "3 4 +"

    def test_simple_subtract(self):
        assert infix_to_rpn("5 - 2") == "5 2 -"

    def test_simple_multiply(self):
        assert infix_to_rpn("3 * 4") == "3 4 *"

    def test_simple_divide(self):
        assert infix_to_rpn("8 / 2") == "8 2 /"

    def test_simple_power(self):
        assert infix_to_rpn("2 ^ 3") == "2 3 ^"


class TestPrecedenceAndParens:
    def test_add_then_mul_no_parens(self):
        # 3 + 4 * 2 → mul binds tighter
        assert infix_to_rpn("3 + 4 * 2") == "3 4 2 * +"

    def test_parens_override(self):
        # (3 + 4) * 2
        assert infix_to_rpn("(3 + 4) * 2") == "3 4 + 2 *"

    def test_nested_parens(self):
        assert infix_to_rpn("((2 + 3))") == "2 3 +"


class TestRightAssocPower:
    def test_right_assoc_chain(self):
        # 2 ^ 3 ^ 2 → 2 ^ (3 ^ 2) = 2 3 2 ^ ^
        assert infix_to_rpn("2 ^ 3 ^ 2") == "2 3 2 ^ ^"

    def test_power_with_parens(self):
        # 2 ^ (3 + 1)
        assert infix_to_rpn("2 ^ (3 + 1)") == "2 3 1 + ^"


class TestFunctions:
    def test_sin_zero(self):
        assert infix_to_rpn("sin(0)") == "0 sin"

    def test_cos(self):
        assert infix_to_rpn("cos(0)") == "0 cos"

    def test_tan(self):
        assert infix_to_rpn("tan(0)") == "0 tan"

    def test_log(self):
        assert infix_to_rpn("log(100)") == "100 log"

    def test_function_with_expr_arg(self):
        # sin(3 + 4)
        assert infix_to_rpn("sin(3 + 4)") == "3 4 + sin"

    def test_function_in_larger_expr(self):
        # sin(3 + 4) * 2
        assert infix_to_rpn("sin(3 + 4) * 2") == "3 4 + sin 2 *"


class TestComplexExpressions:
    def test_log_plus_two(self):
        assert infix_to_rpn("log(100) + 2") == "100 log 2 +"

    def test_multi_operator_chain(self):
        # 1 + 2 * 3 - 4 / 2
        assert infix_to_rpn("1 + 2 * 3 - 4 / 2") == "1 2 3 * + 4 2 / -"
