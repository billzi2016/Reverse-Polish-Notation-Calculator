"""
Operator and function registry — single source of truth for precedence,
associativity, and arity. All other modules import from here exclusively.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Operator:
    symbol: str
    precedence: int
    associativity: Literal["left", "right"]
    arity: int


@dataclass(frozen=True)
class Function:
    name: str
    arity: int


# Binary operators in ascending precedence order
OPERATORS: dict[str, Operator] = {
    "+": Operator(symbol="+", precedence=1, associativity="left",  arity=2),
    "-": Operator(symbol="-", precedence=1, associativity="left",  arity=2),
    "*": Operator(symbol="*", precedence=2, associativity="left",  arity=2),
    "/": Operator(symbol="/", precedence=2, associativity="left",  arity=2),
    "^": Operator(symbol="^", precedence=3, associativity="right", arity=2),
}

# Unary functions — precedence 4 (highest, bind tightest)
FUNCTIONS: dict[str, Function] = {
    "sin": Function(name="sin", arity=1),
    "cos": Function(name="cos", arity=1),
    "tan": Function(name="tan", arity=1),
    "log": Function(name="log", arity=1),   # base-10 logarithm
}

FUNCTION_PRECEDENCE = 4


def is_operator(token: str) -> bool:
    return token in OPERATORS


def is_function(token: str) -> bool:
    return token in FUNCTIONS


def get_precedence(token: str) -> int:
    if token in OPERATORS:
        return OPERATORS[token].precedence
    if token in FUNCTIONS:
        return FUNCTION_PRECEDENCE
    raise ValueError(f"Unknown operator or function: {token!r}")


def is_left_associative(token: str) -> bool:
    if token in OPERATORS:
        return OPERATORS[token].associativity == "left"
    raise ValueError(f"Not a binary operator: {token!r}")
