# 文档树 — 逆波兰科学计算器

## 项目目录结构

```
Reverse-Polish-Notation-Calculator/
│
├── PRD.md                          # 产品需求文档
├── doc-tree.md                     # 本文件：目录结构说明
├── README.md                       # 项目说明与快速启动
├── requirements.txt                # Python 依赖
├── pyproject.toml                  # 项目配置（black / flake8 / pytest）
│
├── src/                            # 源代码根目录
│   │
│   ├── core/                       # 核心算法层
│   │   ├── __init__.py
│   │   ├── operators.py            # ★ 运算符优先级、结合性、元数定义
│   │   ├── tokenizer.py            # 词法分析器：字符串 → Token[]
│   │   ├── parser.py               # 语法分析器：Token[] → AST
│   │   ├── rpn_converter.py        # 转换器：AST → RPN 字符串
│   │   └── evaluator.py            # 求值器：RPN → 数值结果
│   │
│   ├── ast_tree/                   # AST 数据结构与可视化层
│   │   ├── __init__.py
│   │   ├── nodes.py                # AST 节点类定义（NumberNode / OpNode / FuncNode）
│   │   └── visualizer.py          # AST → JPG 渲染（标题：原式 + RPN）
│   │
│   └── ui/                         # 用户交互层
│       ├── __init__.py
│       └── calculator.py           # CLI 主入口（输入 → 全流程 → 输出）
│
├── tests/                          # TDD 测试套件
│   ├── __init__.py
│   ├── conftest.py                 # pytest fixtures 公共配置
│   ├── test_operators.py           # 测试优先级表与结合性规则
│   ├── test_tokenizer.py           # 测试词法分析（正常 + 边界 + 异常）
│   ├── test_parser.py              # 测试 AST 构建（结构断言）
│   ├── test_rpn_converter.py       # 测试 RPN 转换（字符串比对）
│   ├── test_evaluator.py           # 测试数值求值（浮点 + 异常）
│   └── test_visualizer.py          # 测试 JPG 生成（文件存在 + 标题内容）
│
└── output/                         # 运行时生成目录（不提交 JPG 到 git）
    └── trees/
        ├── sin_3+4__2.jpg          # 示例：sin(3+4)*2 的 AST 图
        ├── 2^(3+1).jpg
        └── ...                     # 每次运算自动写入
```

---

## 模块职责说明

### `src/core/operators.py` — 唯一权威来源

```python
# 所有运算符的完整规格，其他模块只 import 此文件，不硬编码优先级
OPERATORS = {
    '+': Operator(symbol='+', precedence=1, associativity='left',  arity=2),
    '-': Operator(symbol='-', precedence=1, associativity='left',  arity=2),
    '*': Operator(symbol='*', precedence=2, associativity='left',  arity=2),
    '/': Operator(symbol='/', precedence=2, associativity='left',  arity=2),
    '^': Operator(symbol='^', precedence=3, associativity='right', arity=2),
}

FUNCTIONS = {
    'sin': Function(name='sin', arity=1),
    'cos': Function(name='cos', arity=1),
    'tan': Function(name='tan', arity=1),
    'log': Function(name='log', arity=1),   # log10
}
```

### `src/core/tokenizer.py`

```
输入：  "sin(3 + 4) * 2"
输出：  [Token(FUNC,'sin'), Token(LPAREN,'('), Token(NUM,'3'),
         Token(OP,'+'), Token(NUM,'4'), Token(RPAREN,')'),
         Token(OP,'*'), Token(NUM,'2')]
```

### `src/core/parser.py`

```
输入：  Token[]
输出：  ASTNode（根节点）

算法：  递归下降 / Pratt 解析（按 operators.py 中的优先级）
```

### `src/core/rpn_converter.py`

```
输入：  ASTNode（根节点）
输出：  "3 4 + sin 2 *"

算法：  后序遍历 AST
```

### `src/core/evaluator.py`

```
输入：  RPN 字符串 "3 4 + sin 2 *"
输出：  1.9799...

算法：  基于栈的 RPN 求值
```

### `src/ast_tree/nodes.py`

```python
@dataclass
class NumberNode:
    value: float

@dataclass
class OperatorNode:
    symbol: str
    left: ASTNode
    right: ASTNode

@dataclass
class FunctionNode:
    name: str
    argument: ASTNode

ASTNode = NumberNode | OperatorNode | FunctionNode
```

### `src/ast_tree/visualizer.py`

```
输入：  ASTNode, infix_expr: str, rpn_expr: str, output_path: str
输出：  JPG 文件

布局：
  ┌──────────────────────────────────────────┐
  │  sin(3 + 4) * 2                          │  ← 标题行 1（原式）
  │  RPN: 3 4 + sin 2 *                      │  ← 标题行 2（逆波兰）
  ├──────────────────────────────────────────┤
  │                   *                      │
  │                  / \                     │
  │               sin   2                    │
  │                |                         │
  │                +                         │
  │               / \                        │
  │              3   4                       │
  └──────────────────────────────────────────┘
```

---

## TDD 测试分层策略

```
test_operators.py
  ├── test_precedence_ordering        # + < * < ^
  ├── test_associativity_right        # ^ 是右结合
  └── test_unknown_operator_raises

test_tokenizer.py
  ├── test_simple_arithmetic          # "3 + 4"
  ├── test_function_call              # "sin(0)"
  ├── test_nested_parens              # "((2+3))"
  ├── test_negative_number            # "-5 + 3"
  └── test_invalid_char_raises

test_parser.py
  ├── test_ast_structure_add          # 断言树形结构
  ├── test_ast_structure_power        # 右结合
  ├── test_ast_function_wrap          # FunctionNode
  └── test_unmatched_paren_raises

test_rpn_converter.py
  ├── test_rpn_simple                 # "3 + 4" → "3 4 +"
  ├── test_rpn_with_parens            # "(3+4)*2" → "3 4 + 2 *"
  ├── test_rpn_function               # "sin(0)" → "0 sin"
  └── test_rpn_right_assoc_power      # "2^3^2" → "2 3 2 ^ ^"

test_evaluator.py
  ├── test_eval_basic_ops
  ├── test_eval_trig                  # sin/cos/tan
  ├── test_eval_log                   # log(100) == 2
  ├── test_eval_div_by_zero_raises
  └── test_eval_unknown_token_raises

test_visualizer.py
  ├── test_jpg_file_created
  ├── test_title_contains_infix       # 图像标题包含原式
  └── test_title_contains_rpn         # 图像标题包含 RPN
```

---

## 实现顺序（TDD 流程）

```
Phase 1  operators.py        → test_operators.py        ✓ 最先，其余模块依赖它
Phase 2  nodes.py            → （无独立测试，被 parser 测试覆盖）
Phase 3  tokenizer.py        → test_tokenizer.py        ✓
Phase 4  parser.py           → test_parser.py           ✓
Phase 5  rpn_converter.py    → test_rpn_converter.py    ✓
Phase 6  evaluator.py        → test_evaluator.py        ✓
Phase 7  visualizer.py       → test_visualizer.py       ✓
Phase 8  calculator.py       → 集成测试（端到端）       ✓
```
