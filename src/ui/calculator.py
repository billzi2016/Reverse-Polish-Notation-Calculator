"""
CLI entry point for the RPN Scientific Calculator.

Usage:
    python -m src.ui.calculator
    python -m src.ui.calculator "sin(3 + 4) * 2"
"""
from __future__ import annotations
import sys
from pathlib import Path

from src.core.parser import parse
from src.core.rpn_converter import ast_to_rpn
from src.core.evaluator import evaluate_rpn
from src.ast_tree.visualizer import render_ast, expr_to_filename

OUTPUT_DIR = Path("output/trees")


def calculate(infix: str) -> dict:
    """
    Full pipeline: infix → AST → RPN → result → JPG.

    Returns a dict with keys: infix, rpn, result, image_path.
    """
    ast = parse(infix)
    rpn = ast_to_rpn(ast)
    result = evaluate_rpn(rpn)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image_path = OUTPUT_DIR / (expr_to_filename(infix) + ".jpg")
    render_ast(ast, infix, rpn, str(image_path), result=result)

    return {
        "infix":      infix,
        "rpn":        rpn,
        "result":     result,
        "image_path": str(image_path),
    }


def _print_result(data: dict) -> None:
    print(f"\n  Expression : {data['infix']}")
    print(f"  RPN        : {data['rpn']}")
    print(f"  Result     : {data['result']}")
    print(f"  AST image  : {data['image_path']}\n")


def _repl() -> None:
    print("RPN Scientific Calculator  (type 'quit' to exit)")
    print("Supported: + - * / ^ sin cos tan log and parentheses\n")
    while True:
        try:
            expr = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if expr.lower() in ("quit", "exit", "q"):
            break
        if not expr:
            continue
        try:
            _print_result(calculate(expr))
        except Exception as e:
            print(f"  Error: {e}\n")


def main() -> None:
    if len(sys.argv) > 1:
        expr = " ".join(sys.argv[1:])
        try:
            _print_result(calculate(expr))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        _repl()


if __name__ == "__main__":
    main()
