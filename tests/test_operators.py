import pytest
from src.core.operators import (
    OPERATORS, FUNCTIONS, get_precedence, is_left_associative,
    is_operator, is_function,
)


class TestPrecedenceOrdering:
    def test_add_less_than_multiply(self):
        assert OPERATORS["+"].precedence < OPERATORS["*"].precedence

    def test_subtract_less_than_divide(self):
        assert OPERATORS["-"].precedence < OPERATORS["/"].precedence

    def test_multiply_less_than_power(self):
        assert OPERATORS["*"].precedence < OPERATORS["^"].precedence

    def test_add_equals_subtract(self):
        assert OPERATORS["+"].precedence == OPERATORS["-"].precedence

    def test_multiply_equals_divide(self):
        assert OPERATORS["*"].precedence == OPERATORS["/"].precedence

    def test_function_highest_precedence(self):
        for op in OPERATORS.values():
            assert get_precedence("sin") > op.precedence


class TestAssociativity:
    def test_add_is_left(self):
        assert is_left_associative("+") is True

    def test_subtract_is_left(self):
        assert is_left_associative("-") is True

    def test_multiply_is_left(self):
        assert is_left_associative("*") is True

    def test_divide_is_left(self):
        assert is_left_associative("/") is True

    def test_power_is_right(self):
        assert OPERATORS["^"].associativity == "right"
        assert is_left_associative("^") is False

    def test_function_not_binary_raises(self):
        with pytest.raises(ValueError):
            is_left_associative("sin")


class TestPredicates:
    def test_is_operator_true(self):
        for sym in ["+", "-", "*", "/", "^"]:
            assert is_operator(sym) is True

    def test_is_operator_false(self):
        assert is_operator("sin") is False
        assert is_operator("x") is False

    def test_is_function_true(self):
        for name in ["sin", "cos", "tan", "log"]:
            assert is_function(name) is True

    def test_is_function_false(self):
        assert is_function("+") is False
        assert is_function("exp") is False


class TestGetPrecedence:
    def test_known_operator(self):
        assert get_precedence("+") == 1
        assert get_precedence("^") == 3

    def test_known_function(self):
        assert get_precedence("sin") == 4

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown"):
            get_precedence("@")


class TestArity:
    def test_binary_operators_arity_2(self):
        for op in OPERATORS.values():
            assert op.arity == 2

    def test_functions_arity_1(self):
        for fn in FUNCTIONS.values():
            assert fn.arity == 1
