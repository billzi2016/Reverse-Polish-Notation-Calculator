import math
import pytest
from src.core.evaluator import evaluate_rpn


class TestBasicOperations:
    def test_add(self):
        assert evaluate_rpn("3 4 +") == 7.0

    def test_subtract(self):
        assert evaluate_rpn("5 2 -") == 3.0

    def test_multiply(self):
        assert evaluate_rpn("3 4 *") == 12.0

    def test_divide(self):
        assert evaluate_rpn("8 2 /") == 4.0

    def test_power(self):
        assert evaluate_rpn("2 3 ^") == 8.0


class TestComplexExpressions:
    def test_parens_expr(self):
        # (3 + 4) * 2 = 14
        assert evaluate_rpn("3 4 + 2 *") == 14.0

    def test_precedence_expr(self):
        # 3 + 4 * 2 = 11
        assert evaluate_rpn("3 4 2 * +") == 11.0

    def test_right_assoc_power(self):
        # 2 ^ (3 ^ 2) = 2^9 = 512
        assert evaluate_rpn("2 3 2 ^ ^") == 512.0

    def test_power_with_sum(self):
        # 2 ^ (3 + 1) = 16
        assert evaluate_rpn("2 3 1 + ^") == 16.0

    def test_multi_operator(self):
        # 1 + 2 * 3 - 4 / 2 = 1 + 6 - 2 = 5
        assert evaluate_rpn("1 2 3 * + 4 2 / -") == 5.0


class TestTrigonometry:
    def test_sin_zero(self):
        assert evaluate_rpn("0 sin") == pytest.approx(0.0)

    def test_cos_zero(self):
        assert evaluate_rpn("0 cos") == pytest.approx(1.0)

    def test_tan_zero(self):
        assert evaluate_rpn("0 tan") == pytest.approx(0.0)

    def test_sin_pi_over_2(self):
        half_pi = math.pi / 2
        assert evaluate_rpn(f"{half_pi} sin") == pytest.approx(1.0)

    def test_sin_in_expr(self):
        # sin(3 + 4) * 2
        result = evaluate_rpn("3 4 + sin 2 *")
        assert result == pytest.approx(math.sin(7) * 2)


class TestLog:
    def test_log_100(self):
        assert evaluate_rpn("100 log") == pytest.approx(2.0)

    def test_log_1(self):
        assert evaluate_rpn("1 log") == pytest.approx(0.0)

    def test_log_in_expr(self):
        # log(100) + 2 = 4
        assert evaluate_rpn("100 log 2 +") == pytest.approx(4.0)


class TestErrors:
    def test_div_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            evaluate_rpn("5 0 /")

    def test_unknown_token_raises(self):
        with pytest.raises(ValueError, match="Unknown token"):
            evaluate_rpn("3 4 @")

    def test_too_many_operands_raises(self):
        with pytest.raises(ValueError, match="Malformed RPN"):
            evaluate_rpn("3 4 5 +")

    def test_missing_operand_raises(self):
        with pytest.raises(ValueError):
            evaluate_rpn("3 +")
