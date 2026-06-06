"""Lexical analyzer: converts an expression string into a token list."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
import re

from src.core.operators import is_operator, is_function


class TokenType(Enum):
    NUMBER   = auto()
    OPERATOR = auto()
    FUNCTION = auto()
    LPAREN   = auto()
    RPAREN   = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r})"


_TOKEN_RE = re.compile(
    r"""
    (?P<NUMBER>   -?\d+(?:\.\d+)?)  |  # integer or decimal (optional leading -)
    (?P<FUNC>     [a-zA-Z]+)         |  # function name
    (?P<OP>       [+\-*/^])          |  # binary operator
    (?P<LPAREN>   \()                |  # left parenthesis
    (?P<RPAREN>   \))                |  # right parenthesis
    (?P<SPACE>    \s+)               |  # whitespace (ignored)
    (?P<INVALID>  .)                    # anything else → error
    """,
    re.VERBOSE,
)


def tokenize(expr: str) -> list[Token]:
    """
    Convert an infix expression string into a list of Tokens.

    Raises:
        ValueError: on unknown characters or unknown function names.
    """
    tokens: list[Token] = []
    prev_type: TokenType | None = None

    for match in _TOKEN_RE.finditer(expr):
        kind = match.lastgroup
        raw  = match.group()

        if kind == "SPACE":
            continue

        if kind == "INVALID":
            raise ValueError(f"Unexpected character {raw!r} in expression")

        if kind == "NUMBER":
            # A bare '-' after an operator/open-paren is unary; the regex above
            # captures it as part of the number token.  But if we already saw a
            # number or ')', the '-' belongs to the NEXT token as an operator.
            # Re-split in that edge case.
            if raw.startswith("-") and prev_type in (TokenType.NUMBER, TokenType.RPAREN):
                tokens.append(Token(TokenType.OPERATOR, "-"))
                raw = raw[1:]
            tokens.append(Token(TokenType.NUMBER, raw))
            prev_type = TokenType.NUMBER

        elif kind == "FUNC":
            if not is_function(raw):
                raise ValueError(f"Unknown function {raw!r}")
            tokens.append(Token(TokenType.FUNCTION, raw))
            prev_type = TokenType.FUNCTION

        elif kind == "OP":
            # Unary minus: '-' at start, or after '(' or another operator
            if raw == "-" and prev_type not in (TokenType.NUMBER, TokenType.RPAREN):
                # Treat as part of next number; peek ahead is not straightforward,
                # so we push a synthetic 0 and a '-' operator for unary minus.
                tokens.append(Token(TokenType.NUMBER, "0"))
                tokens.append(Token(TokenType.OPERATOR, "-"))
                prev_type = TokenType.OPERATOR
            else:
                tokens.append(Token(TokenType.OPERATOR, raw))
                prev_type = TokenType.OPERATOR

        elif kind == "LPAREN":
            tokens.append(Token(TokenType.LPAREN, "("))
            prev_type = TokenType.LPAREN

        elif kind == "RPAREN":
            tokens.append(Token(TokenType.RPAREN, ")"))
            prev_type = TokenType.RPAREN

    return tokens
