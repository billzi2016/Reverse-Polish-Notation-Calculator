"""Convert an AST to a Reverse Polish Notation string via post-order traversal."""
from src.ast_tree.nodes import ASTNode, NumberNode, OperatorNode, FunctionNode
from src.core.parser import parse as _parse


def ast_to_rpn(node: ASTNode) -> str:
    """Post-order traversal of the AST → space-separated RPN token string."""
    tokens: list[str] = []
    _traverse(node, tokens)
    return " ".join(tokens)


def _traverse(node: ASTNode, out: list[str]) -> None:
    if isinstance(node, NumberNode):
        v = int(node.value) if node.value == int(node.value) else node.value
        out.append(str(v))

    elif isinstance(node, OperatorNode):
        _traverse(node.left,  out)
        _traverse(node.right, out)
        out.append(node.symbol)

    elif isinstance(node, FunctionNode):
        _traverse(node.argument, out)
        out.append(node.name)

    else:
        raise TypeError(f"Unknown AST node type: {type(node)}")


def infix_to_rpn(expr: str) -> str:
    """Convenience: infix string → RPN string."""
    return ast_to_rpn(_parse(expr))
