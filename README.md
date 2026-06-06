# RPN Scientific Calculator

A scientific calculator that converts infix expressions into **Reverse Polish Notation (RPN)** and visualizes the underlying **Abstract Syntax Tree (AST)** as a labeled diagram image.

---

## What is Reverse Polish Notation?

Standard math writes operators *between* operands — this is called **infix** notation:

```
3 + 4
(3 + 4) * 2
sin(3 + 4) * 2
```

**Reverse Polish Notation** places operators *after* their operands — no parentheses needed, because the order of operands already encodes structure:

```
3 4 +
3 4 + 2 *
3 4 + sin 2 *
```

A simple stack machine can evaluate any RPN expression in one linear pass:

1. Read tokens left to right
2. Push numbers onto the stack
3. When an operator appears, pop its operands, apply it, push the result

For `3 4 + 2 *`:

```
token  stack
3      [3]
4      [3, 4]
+      [7]        ← pop 3,4 → push 3+4
2      [7, 2]
*      [14]       ← pop 7,2 → push 7*2
```

Result: **14**

---

## How It Works

```
Input string  →  Tokenizer  →  Parser  →  AST
                                            │
                              ┌─────────────┤
                              │             │
                         RPN Converter  Evaluator
                              │
                          Visualizer → JPG
```

| Stage | Input | Output |
|-------|-------|--------|
| **Tokenizer** | `"sin(3 + 4) * 2"` | `[FUNC:sin, LPAREN, NUM:3, OP:+, NUM:4, RPAREN, OP:*, NUM:2]` |
| **Parser** | token list | AST (tree of nodes) |
| **RPN Converter** | AST root | `"3 4 + sin 2 *"` |
| **Evaluator** | RPN string | `1.31397` |
| **Visualizer** | AST + labels | `.jpg` image |

### Operator Precedence (defined in `src/core/operators.py`)

| Symbol | Type | Precedence | Associativity |
|--------|------|-----------|---------------|
| `+` `-` | binary | 1 | left |
| `*` `/` | binary | 2 | left |
| `^` | binary | 3 | **right** |
| `sin` `cos` `tan` `log` | unary function | 4 (highest) | — |

Right-associativity of `^` means `2 ^ 3 ^ 2` parses as `2 ^ (3 ^ 2)` = 512, not `(2 ^ 3) ^ 2` = 64.

---

## Supported Expressions

| Expression | RPN | Result |
|-----------|-----|--------|
| `3 + 4` | `3 4 +` | `7` |
| `(3 + 4) * 2` | `3 4 + 2 *` | `14` |
| `2 ^ 3` | `2 3 ^` | `8` |
| `2 ^ 3 ^ 2` | `2 3 2 ^ ^` | `512` |
| `sin(0)` | `0 sin` | `0` |
| `cos(0)` | `0 cos` | `1` |
| `log(100)` | `100 log` | `2` |
| `log(100) + 2` | `100 log 2 +` | `4` |
| `sin(3 + 4) * 2` | `3 4 + sin 2 *` | `1.31397` |
| `(2 + 3) * (4 - 1) ^ 2` | `2 3 + 4 1 - 2 ^ *` | `45` |

---

## AST Visualization

Every calculation produces a `.jpg` image saved to `output/trees/`.

The image has three header lines:

```
sin(3 + 4) * 2          ← original infix expression
RPN:    3 4 + sin 2 *   ← reverse polish notation
Result: 1.31397         ← computed value
──────────────────────────────
         [tree diagram]
```

- **Orange rounded rectangles** — operators and functions (internal nodes)
- **Blue circles** — numbers (leaf nodes)
- **Arrows** — parent → child direction

### Example: `sin(3 + 4) * 2`

```
           *
          / \
        sin   2
         |
         +
        / \
       3   4
```

The tree encodes evaluation order: to compute `*`, we need `sin` first; to compute `sin`, we need `+` first; `+` needs `3` and `4`. Post-order traversal of this tree yields the RPN string directly.

---

## Installation

```bash
git clone https://github.com/<you>/Reverse-Polish-Notation-Calculator.git
cd Reverse-Polish-Notation-Calculator
pip install -r requirements.txt
```

---

## Usage

### Interactive REPL

```bash
python -m src.ui.calculator
```

```
RPN Scientific Calculator  (type 'quit' to exit)
Supported: + - * / ^ sin cos tan log and parentheses

>> sin(3 + 4) * 2

  Expression : sin(3 + 4) * 2
  RPN        : 3 4 + sin 2 *
  Result     : 1.3139731974375781
  AST image  : output/trees/sin(3_+_4)_*_2.jpg

>> (2 + 3) * (4 - 1) ^ 2

  Expression : (2 + 3) * (4 - 1) ^ 2
  RPN        : 2 3 + 4 1 - 2 ^ *
  Result     : 45.0
  AST image  : output/trees/(2_+_3)_*_(4_-_1)_^_2.jpg

>> quit
```

### Single Expression

```bash
python -m src.ui.calculator "log(100) + 2"
```

```
  Expression : log(100) + 2
  RPN        : 100 log 2 +
  Result     : 4.0
  AST image  : output/trees/log(100)_+_2.jpg
```

### Python API

```python
from src.ui.calculator import calculate

result = calculate("(2 + 3) * (4 - 1) ^ 2")
print(result["rpn"])        # 2 3 + 4 1 - 2 ^ *
print(result["result"])     # 45.0
print(result["image_path"]) # output/trees/(2_+_3)_*_(4_-_1)_^_2.jpg
```

Or use individual stages:

```python
from src.core.parser       import parse
from src.core.rpn_converter import ast_to_rpn
from src.core.evaluator    import evaluate_rpn
from src.ast_tree.visualizer import render_ast

ast    = parse("2 ^ 3 ^ 2")
rpn    = ast_to_rpn(ast)          # "2 3 2 ^ ^"
result = evaluate_rpn(rpn)        # 512.0
render_ast(ast, "2 ^ 3 ^ 2", rpn, "output/trees/power.jpg", result=result)
```

---

## Running Tests

```bash
# All tests with coverage report
python -m pytest tests/ -v

# Single module
python -m pytest tests/test_rpn_converter.py -v
```

107 tests cover every module: tokenizer, parser, RPN converter, evaluator, and visualizer.

---

## Project Structure

```
src/
├── core/
│   ├── operators.py       ← single source of truth: precedence & associativity
│   ├── tokenizer.py       ← string → token list
│   ├── parser.py          ← token list → AST (Pratt / recursive descent)
│   ├── rpn_converter.py   ← AST → RPN string (post-order traversal)
│   └── evaluator.py       ← RPN string → float (stack machine)
├── ast_tree/
│   ├── nodes.py           ← NumberNode / OperatorNode / FunctionNode
│   └── visualizer.py      ← AST → JPG (matplotlib)
└── ui/
    └── calculator.py      ← CLI entry point

tests/
├── test_operators.py
├── test_tokenizer.py
├── test_parser.py
├── test_rpn_converter.py
├── test_evaluator.py
└── test_visualizer.py

output/
└── trees/                 ← generated JPG images (one per expression)
```

---

## Error Handling

| Input | Error |
|-------|-------|
| `3 @ 4` | `ValueError: Unexpected character '@'` |
| `exp(1)` | `ValueError: Unknown function 'exp'` |
| `(3 + 4` | `ValueError: Expected RPAREN` |
| `5 / 0` | `ZeroDivisionError: Division by zero` |
| `3 +` | `ValueError: Malformed RPN` |
