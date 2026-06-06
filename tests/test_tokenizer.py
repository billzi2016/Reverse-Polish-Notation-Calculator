import pytest
from src.core.tokenizer import tokenize, Token, TokenType


def toks(expr: str) -> list[tuple[str, str]]:
    """Helper: return (type_name, value) pairs."""
    return [(t.type.name, t.value) for t in tokenize(expr)]


class TestSimpleArithmetic:
    def test_addition(self):
        result = toks("3 + 4")
        assert result == [("NUMBER", "3"), ("OPERATOR", "+"), ("NUMBER", "4")]

    def test_no_spaces(self):
        result = toks("3+4")
        assert result == [("NUMBER", "3"), ("OPERATOR", "+"), ("NUMBER", "4")]

    def test_all_binary_operators(self):
        for op in ["+", "-", "*", "/", "^"]:
            result = toks(f"1{op}2")
            assert result[1] == ("OPERATOR", op)

    def test_float_number(self):
        result = toks("3.14 + 2.0")
        assert result[0] == ("NUMBER", "3.14")


class TestFunctionTokens:
    def test_sin(self):
        result = toks("sin(0)")
        assert result[0] == ("FUNCTION", "sin")
        assert result[1] == ("LPAREN",   "(")
        assert result[2] == ("NUMBER",   "0")
        assert result[3] == ("RPAREN",   ")")

    def test_all_functions(self):
        for fn in ["sin", "cos", "tan", "log"]:
            result = toks(f"{fn}(1)")
            assert result[0] == ("FUNCTION", fn)

    def test_unknown_function_raises(self):
        with pytest.raises(ValueError, match="Unknown function"):
            tokenize("exp(1)")


class TestParentheses:
    def test_nested_parens(self):
        result = toks("((2+3))")
        assert result[0] == ("LPAREN",   "(")
        assert result[1] == ("LPAREN",   "(")
        assert result[-1] == ("RPAREN",  ")")
        assert result[-2] == ("RPAREN",  ")")

    def test_complex_expr(self):
        result = toks("(3 + 4) * 2")
        types = [t[0] for t in result]
        assert types == ["LPAREN", "NUMBER", "OPERATOR", "NUMBER",
                         "RPAREN", "OPERATOR", "NUMBER"]


class TestUnaryMinus:
    def test_unary_minus_at_start(self):
        # "-5 + 3" → -5 is a negative number literal
        result = toks("-5 + 3")
        assert result[0] == ("NUMBER",   "-5")
        assert result[1] == ("OPERATOR", "+")
        assert result[2] == ("NUMBER",   "3")

    def test_unary_minus_after_lparen(self):
        result = toks("(-5)")
        assert result[0] == ("LPAREN",   "(")
        assert result[1] == ("NUMBER",   "-5")
        assert result[2] == ("RPAREN",   ")")


class TestInvalidInput:
    def test_invalid_char_raises(self):
        with pytest.raises(ValueError, match="Unexpected character"):
            tokenize("3 @ 4")

    def test_empty_string_returns_empty(self):
        assert tokenize("") == []
