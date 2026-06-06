"""
Render an AST to a JPG image.

Layout:
  Line 1  — original infix expression
  Line 2  — RPN: <rpn expression>
  Line 3  — Result: <value>
  Below   — tree diagram drawn with matplotlib
"""
from __future__ import annotations
import os
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

from src.ast_tree.nodes import ASTNode, NumberNode, OperatorNode, FunctionNode


# ── node layout ──────────────────────────────────────────────────────────────

def _label(node: ASTNode) -> str:
    if isinstance(node, NumberNode):
        v = int(node.value) if node.value == int(node.value) else node.value
        return str(v)
    elif isinstance(node, OperatorNode):
        return node.symbol
    elif isinstance(node, FunctionNode):
        return node.name
    return "?"


def _children(node: ASTNode) -> list[ASTNode]:
    if isinstance(node, OperatorNode):
        return [node.left, node.right]
    elif isinstance(node, FunctionNode):
        return [node.argument]
    return []


def _assign_positions(
    node: ASTNode,
    depth: int = 0,
    counter: list[int] | None = None,
) -> dict[int, tuple[float, float]]:
    """Return {id(node): (x, y)} via in-order position assignment."""
    if counter is None:
        counter = [0]
    positions: dict[int, tuple[float, float]] = {}
    kids = _children(node)

    if kids:
        positions.update(_assign_positions(kids[0], depth + 1, counter))

    x = counter[0]
    counter[0] += 1
    positions[id(node)] = (x, -depth)

    if len(kids) == 2:
        positions.update(_assign_positions(kids[1], depth + 1, counter))

    return positions


def _collect_edges(
    node: ASTNode,
    positions: dict[int, tuple[float, float]],
    edges: list[tuple[tuple[float, float], tuple[float, float]]] | None = None,
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    if edges is None:
        edges = []
    px, py = positions[id(node)]
    for child in _children(node):
        cx, cy = positions[id(child)]
        edges.append(((px, py), (cx, cy)))
        _collect_edges(child, positions, edges)
    return edges


# ── main render ───────────────────────────────────────────────────────────────

# Node geometry constants
_NODE_R       = 0.30   # circle radius for leaf nodes  (compact)
_BOX_W        = 0.40   # box half-width for operator/function nodes
_BOX_H        = 0.26   # box half-height
_ARROW_OFFSET = 0.36   # how far from node centre the arrow starts/ends


def render_ast(
    node: ASTNode,
    infix_expr: str,
    rpn_expr: str,
    output_path: str,
    result: float | None = None,
) -> None:
    """
    Draw the AST as a JPG.

    Args:
        node:        Root of the AST.
        infix_expr:  Original infix expression (title line 1).
        rpn_expr:    RPN string (title line 2).
        output_path: Destination file path (.jpg).
        result:      Numeric evaluation result shown in the header (line 3).
    """
    positions = _assign_positions(node)
    edges     = _collect_edges(node, positions)

    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    x_min, x_max = min(xs) - 1.2, max(xs) + 1.2
    y_min, y_max = min(ys) - 1.0, max(ys) + 1.0

    # Header height — 3 compact lines
    header_h = 1.3

    fig_w = max(12, (x_max - x_min) * 1.8)
    fig_h = max(9,  (y_max - y_min) * 2.4 + header_h + 1.0)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min - 0.6, y_max + header_h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    cx = (x_min + x_max) / 2

    # ── header (3 lines, tight spacing) ─────────────────────────────────────
    ax.text(
        cx, y_max + 1.10,
        infix_expr,
        ha="center", va="center",
        fontsize=28, fontweight="bold",
        fontfamily="monospace",
        color="#1a1a2e",
    )
    ax.text(
        cx, y_max + 0.70,
        f"RPN:    {rpn_expr}",
        ha="center", va="center",
        fontsize=22,
        fontfamily="monospace",
        color="#2c3e6e",
    )
    if result is not None:
        result_str = str(int(result)) if result == int(result) else f"{result:.6g}"
        ax.text(
            cx, y_max + 0.32,
            f"Result: {result_str}",
            ha="center", va="center",
            fontsize=22, fontweight="bold",
            fontfamily="monospace",
            color="#1a7a3c",
        )

    # Separator line
    sep_y = y_max + 0.02
    ax.plot(
        [x_min + 0.1, x_max - 0.1], [sep_y, sep_y],
        color="#aaaaaa", linewidth=2.0, solid_capstyle="round",
    )

    # ── edges ────────────────────────────────────────────────────────────────
    for (px, py), (child_x, child_y) in edges:
        ax.annotate(
            "",
            xy=(child_x, child_y + _ARROW_OFFSET),
            xytext=(px,    py    - _ARROW_OFFSET),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#44446e",
                lw=3.0,
                mutation_scale=28,   # controls arrow head size
            ),
            zorder=2,
        )

    # ── nodes ────────────────────────────────────────────────────────────────
    for nid, (x, y) in positions.items():
        label   = _find_label_by_id(node, nid) or "?"
        is_leaf = bool(_is_leaf_id(node, nid))

        if is_leaf:
            circle = plt.Circle(
                (x, y), _NODE_R,
                facecolor="#ddeeff", edgecolor="#2a6db5",
                linewidth=3.0, zorder=3,
            )
            ax.add_patch(circle)
            ax.text(
                x, y, label,
                ha="center", va="center",
                fontsize=22, fontfamily="monospace",
                fontweight="bold", color="#0d2b5e", zorder=4,
            )
        else:
            box = FancyBboxPatch(
                (x - _BOX_W, y - _BOX_H), _BOX_W * 2, _BOX_H * 2,
                boxstyle="round,pad=0.08",
                facecolor="#fff3e0", edgecolor="#e65c00",
                linewidth=3.0, zorder=3,
            )
            ax.add_patch(box)
            ax.text(
                x, y, label,
                ha="center", va="center",
                fontsize=24, fontfamily="monospace",
                fontweight="bold", color="#c0392b", zorder=4,
            )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.tight_layout(pad=0.4)
    plt.savefig(
        output_path, format="jpeg", dpi=130,
        bbox_inches="tight", facecolor="white",
    )
    plt.close(fig)


# ── helpers ──────────────────────────────────────────────────────────────────

def _find_label_by_id(root: ASTNode, target_id: int) -> str | None:
    if id(root) == target_id:
        return _label(root)
    for child in _children(root):
        result = _find_label_by_id(child, target_id)
        if result is not None:
            return result
    return None


def _is_leaf_id(root: ASTNode, target_id: int) -> bool | None:
    if id(root) == target_id:
        return isinstance(root, NumberNode)
    for child in _children(root):
        result = _is_leaf_id(child, target_id)
        if result is not None:
            return result
    return None


# ── filename sanitize ────────────────────────────────────────────────────────

def expr_to_filename(expr: str) -> str:
    safe = re.sub(r"[^\w\-+*/^()]", "_", expr)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe[:80]
