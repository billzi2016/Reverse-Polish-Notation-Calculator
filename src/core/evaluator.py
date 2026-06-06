"""Stack-based RPN evaluator."""
from __future__ import annotations
import math
from src.core.operators import is_operator, is_function


_BINARY_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: (_ for _ in ()).throw(ZeroDivisionError("Division by zero"))
         if b == 0 else a / b,
    "^": lambda a, b: a ** b,
}

_UNARY_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log10,
}


def evaluate_rpn(rpn: str) -> float:
    """
    Evaluate a space-separated RPN expression string.

    Raises:
        ZeroDivisionError: on division by zero.
        ValueError: on malformed RPN or unknown token.
    """
    stack: list[float] = []

    for token in rpn.split():
        if _is_number(token):
            stack.append(float(token))

        elif token in _BINARY_OPS:
            if len(stack) < 2:
                raise ValueError(f"Not enough operands for operator {token!r}")
            b = stack.pop()
            a = stack.pop()
            if token == "/" and b == 0:
                raise ZeroDivisionError("Division by zero")
            stack.append(_BINARY_OPS[token](a, b))

        elif token in _UNARY_FUNCS:
            if not stack:
                raise ValueError(f"Not enough operands for function {token!r}")
            a = stack.pop()
            stack.append(_UNARY_FUNCS[token](a))

        else:
            raise ValueError(f"Unknown token in RPN: {token!r}")

    if len(stack) != 1:
        raise ValueError(f"Malformed RPN: stack has {len(stack)} elements after evaluation")

    return stack[0]


def _is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False
