"""
Recursive-descent / Pratt parser.
Converts a Token list into an AST using precedence from operators.py.
"""
from __future__ import annotations
from src.core.tokenizer import Token, TokenType, tokenize
from src.core.operators import get_precedence, is_left_associative, is_operator, is_function
from src.ast_tree.nodes import ASTNode, NumberNode, OperatorNode, FunctionNode


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # ------------------------------------------------------------------ helpers
    def _peek(self) -> Token | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _consume(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, ttype: TokenType) -> Token:
        tok = self._peek()
        if tok is None or tok.type != ttype:
            raise ValueError(
                f"Expected {ttype.name} but got {tok!r} at position {self._pos}"
            )
        return self._consume()

    # ------------------------------------------------------------------ grammar
    def parse(self) -> ASTNode:
        node = self._parse_expr(0)
        if self._peek() is not None:
            raise ValueError(f"Unexpected token {self._peek()!r} after expression")
        return node

    def _parse_expr(self, min_prec: int) -> ASTNode:
        left = self._parse_primary()

        while True:
            tok = self._peek()
            if tok is None or tok.type != TokenType.OPERATOR:
                break
            op = tok.value
            prec = get_precedence(op)
            if prec <= min_prec:
                break
            self._consume()
            # Left-assoc: pass prec as min → equal-precedence stops recursion (left fold)
            # Right-assoc: pass prec-1 as min → equal-precedence continues recursion (right fold)
            right = self._parse_expr(prec - 1 if not is_left_associative(op) else prec)
            left = OperatorNode(symbol=op, left=left, right=right)

        return left

    def _parse_primary(self) -> ASTNode:
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        # Parenthesised sub-expression
        if tok.type == TokenType.LPAREN:
            self._consume()
            node = self._parse_expr(0)
            self._expect(TokenType.RPAREN)
            return node

        # Function call: FUNC ( expr )
        if tok.type == TokenType.FUNCTION:
            self._consume()
            self._expect(TokenType.LPAREN)
            arg = self._parse_expr(0)
            self._expect(TokenType.RPAREN)
            return FunctionNode(name=tok.value, argument=arg)

        # Number literal
        if tok.type == TokenType.NUMBER:
            self._consume()
            return NumberNode(value=float(tok.value))

        raise ValueError(f"Unexpected token {tok!r} at position {self._pos}")


def parse(expr: str) -> ASTNode:
    """Convenience wrapper: infix string → AST."""
    tokens = tokenize(expr)
    return Parser(tokens).parse()
