"""AST node definitions for the RPN calculator."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union


@dataclass
class NumberNode:
    value: float

    def __repr__(self) -> str:
        v = int(self.value) if self.value == int(self.value) else self.value
        return str(v)


@dataclass
class OperatorNode:
    symbol: str
    left: ASTNode
    right: ASTNode

    def __repr__(self) -> str:
        return self.symbol


@dataclass
class FunctionNode:
    name: str
    argument: ASTNode

    def __repr__(self) -> str:
        return self.name


ASTNode = Union[NumberNode, OperatorNode, FunctionNode]
