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

**Reverse Polish Notation (RPN)**, also called **postfix** notation, places operators *after* their operands. No parentheses are needed because the position of operands already encodes the evaluation structure:

```
3 4 +
3 4 + 2 *
3 4 + sin 2 *
```

RPN was introduced by Australian philosopher **Charles Hamblin** in 1957, building on the work of Polish logician **Jan Łukasiewicz**, who invented prefix (Polish) notation in the 1920s. The name "Reverse Polish" reflects that operators come *after* operands, the reverse of Łukasiewicz's scheme.

---

## Two Core Algorithms

This calculator is powered by two classic algorithms, both rooted in Dijkstra's work.

### Algorithm 1 — Dijkstra's Shunting-yard

Invented by **Edsger W. Dijkstra** in 1961, the Shunting-yard algorithm converts an infix expression to RPN (or an AST) in a single left-to-right pass using an **operator stack** and an **output queue**.

```
Input:  3 + 4 * 2
```

| Token | Action | Operator Stack | Output Queue |
|-------|--------|----------------|--------------|
| `3` | number → output | `[]` | `[3]` |
| `+` | push (prec 1) | `[+]` | `[3]` |
| `4` | number → output | `[+]` | `[3, 4]` |
| `*` | prec(*)=2 > prec(+)=1, push | `[+, *]` | `[3, 4]` |
| `2` | number → output | `[+, *]` | `[3, 4, 2]` |
| end | pop remaining | `[]` | `[3, 4, 2, *, +]` |

Result RPN: **`3 4 2 * +`** = 3 + (4 × 2) = **11** ✓

**The key rule:** before pushing an operator `o1`, pop all operators `o2` from the stack where:
- `prec(o2) > prec(o1)`, **or**
- `prec(o2) == prec(o1)` and `o1` is **left-associative**

This naturally handles precedence and associativity without any look-ahead.

For the right-associative `^`, the rule is reversed — equal precedence does **not** trigger a pop:

```
Input:  2 ^ 3 ^ 2
```

| Token | Action | Stack | Output |
|-------|--------|-------|--------|
| `2` | output | `[]` | `[2]` |
| `^` | push | `[^]` | `[2]` |
| `3` | output | `[^]` | `[2, 3]` |
| `^` | prec equal but right-assoc → push | `[^, ^]` | `[2, 3]` |
| `2` | output | `[^, ^]` | `[2, 3, 2]` |
| end | pop both | `[]` | `[2, 3, 2, ^, ^]` |

Result: **`2 3 2 ^ ^`** = 2^(3^2) = 2^9 = **512** ✓

> **This project** uses a **Pratt parser** (recursive descent with precedence climbing) to build an AST directly, then derives RPN via post-order traversal. Pratt parsing and Shunting-yard are equivalent in power — they both encode the same precedence and associativity rules; Pratt operates top-down on the call stack while Shunting-yard operates bottom-up on an explicit stack.

---

### Algorithm 2 — Stack-based RPN Evaluation

Once an expression is in RPN form, evaluation is a single linear pass with a stack:

1. Read tokens left to right
2. **Number** → push onto stack
3. **Operator / function** → pop operands, compute, push result

For `3 4 2 * +`:

```
token  stack
3      [3]
4      [3, 4]
2      [3, 4, 2]
*      [3, 8]      ← pop 4, 2 → push 4*2
+      [11]        ← pop 3, 8 → push 3+8
```

Result: **11**

For `3 4 + sin 2 *`:

```
token  stack
3      [3]
4      [3, 4]
+      [7]         ← pop 3, 4 → push 7
sin    [0.6570]    ← pop 7 → push sin(7)
2      [0.6570, 2]
*      [1.3140]    ← pop 0.6570, 2 → push result
```

Result: **1.3140**

No parentheses, no precedence rules needed — the stack handles everything automatically. This is why RPN was widely used in early calculators and stack-based virtual machines (Forth, JVM, CPython bytecode).

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

### Complex Nested Expressions

| Expression | RPN | Result |
|-----------|-----|--------|
| `sin(cos(1) + 2) * log(100)` | `1 cos 2 + sin 100 log *` | `1.13141` |
| `(sin(1) + cos(1)) ^ 2 + tan(1) * log(10)` | `1 sin 1 cos + 2 ^ 1 tan 10 log * +` | `3.46671` |
| `log(sin(1) * 10 + cos(1) * 10)` | `1 sin 10 * 1 cos 10 * + log` | `1.14044` |
| `sin(1 + cos(1)) * (log(100) + tan(1))` | `1 1 cos + sin 100 log 1 tan + *` | `3.55575` |
| `(sin(1) * cos(1) + log(10)) ^ 2` | `1 sin 1 cos * 10 log + 2 ^` | `2.11600` |
| `cos(sin(1) + tan(1)) * log(100) + sin(1) ^ 2` | `1 sin 1 tan + cos 100 log * 1 sin 2 ^ +` | `-0.76520` |
| `log(100) * (sin(1) + cos(1)) - tan(1) ^ 2` | `100 log 1 sin 1 cos + * 1 tan 2 ^ -` | `0.33803` |

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
