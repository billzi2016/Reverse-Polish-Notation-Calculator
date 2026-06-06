# 逆波兰科学计算器

将中缀表达式转换为**逆波兰表达式（RPN）**，并将底层**抽象语法树（AST）**渲染为带标注的 JPG 图像。

---

## 什么是逆波兰表达式？

普通数学将运算符写在两个操作数**之间**，称为**中缀**表达式：

```
3 + 4
(3 + 4) * 2
sin(3 + 4) * 2
```

**逆波兰表达式（RPN）**，也称**后缀表达式**，将运算符放在操作数**之后**。不需要括号，因为操作数的位置已经完整编码了求值结构：

```
3 4 +
3 4 + 2 *
3 4 + sin 2 *
```

RPN 由澳大利亚哲学家 **Charles Hamblin** 于 1957 年提出，其灵感来自波兰逻辑学家 **扬·武卡谢维奇（Jan Łukasiewicz）** 在 20 世纪 20 年代发明的前缀（波兰）表示法。"逆波兰"之名正是因为运算符写在操作数**之后**，与武卡谢维奇的方案相反。

---

## 两个核心算法

本计算器由两个经典算法驱动，均源自 Dijkstra 的工作。

### 算法一 — Dijkstra 调度场算法（Shunting-yard）

**Edsger W. Dijkstra** 于 1961 年发明，调度场算法只需一趟从左到右的扫描，借助**运算符栈**和**输出队列**，将中缀表达式直接转换为 RPN（或 AST）。

```
输入：3 + 4 * 2
```

| Token | 动作 | 运算符栈 | 输出队列 |
|-------|------|----------|----------|
| `3` | 数字 → 输出 | `[]` | `[3]` |
| `+` | 压栈（优先级 1） | `[+]` | `[3]` |
| `4` | 数字 → 输出 | `[+]` | `[3, 4]` |
| `*` | prec(*)=2 > prec(+)=1，压栈 | `[+, *]` | `[3, 4]` |
| `2` | 数字 → 输出 | `[+, *]` | `[3, 4, 2]` |
| 结束 | 弹出剩余运算符 | `[]` | `[3, 4, 2, *, +]` |

输出 RPN：**`3 4 2 * +`** = 3 + (4 × 2) = **11** ✓

**核心规则：** 压入运算符 `o1` 之前，将栈顶满足以下条件的运算符 `o2` 全部弹出到输出队列：
- `prec(o2) > prec(o1)`，**或**
- `prec(o2) == prec(o1)` 且 `o1` 是**左结合**的

这样可在无需前瞻的情况下，自动处理优先级和结合性。

对于右结合的 `^`，规则反转——相同优先级**不**触发弹出：

```
输入：2 ^ 3 ^ 2
```

| Token | 动作 | 栈 | 输出 |
|-------|------|----|------|
| `2` | 输出 | `[]` | `[2]` |
| `^` | 压栈 | `[^]` | `[2]` |
| `3` | 输出 | `[^]` | `[2, 3]` |
| `^` | 优先级相同但右结合 → 压栈 | `[^, ^]` | `[2, 3]` |
| `2` | 输出 | `[^, ^]` | `[2, 3, 2]` |
| 结束 | 弹出两个 | `[]` | `[2, 3, 2, ^, ^]` |

结果：**`2 3 2 ^ ^`** = 2^(3^2) = 2^9 = **512** ✓

> **本项目**使用 **Pratt 解析器**（带优先级攀升的递归下降）直接构建 AST，再通过后序遍历得到 RPN。Pratt 解析器与调度场算法在能力上等价——两者均编码了相同的优先级和结合性规则；Pratt 在调用栈上自顶向下运作，调度场在显式栈上自底向上运作。

---

### 算法二 — 基于栈的 RPN 求值

表达式转为 RPN 后，求值只需一趟线性扫描加一个栈：

1. 从左到右读取 token
2. **数字** → 压栈
3. **运算符 / 函数** → 弹出操作数，计算，将结果压回

以 `3 4 2 * +` 为例：

```
token  栈
3      [3]
4      [3, 4]
2      [3, 4, 2]
*      [3, 8]      ← 弹出 4, 2 → 压入 4*2
+      [11]        ← 弹出 3, 8 → 压入 3+8
```

结果：**11**

以 `3 4 + sin 2 *` 为例：

```
token  栈
3      [3]
4      [3, 4]
+      [7]         ← 弹出 3, 4 → 压入 7
sin    [0.6570]    ← 弹出 7 → 压入 sin(7)
2      [0.6570, 2]
*      [1.3140]    ← 弹出 0.6570, 2 → 压入结果
```

结果：**1.3140**

无需括号，无需优先级规则——栈自动处理一切。这正是 RPN 在早期计算器和基于栈的虚拟机（Forth、JVM、CPython 字节码）中被广泛采用的原因。

---

## 工作原理

```
输入字符串 → 词法分析器 → 语法分析器 → AST
                                         │
                           ┌─────────────┤
                           │             │
                      RPN 转换器      求值器
                           │
                        可视化器 → JPG
```

| 阶段 | 输入 | 输出 |
|------|------|------|
| **词法分析器** | `"sin(3 + 4) * 2"` | `[FUNC:sin, LPAREN, NUM:3, OP:+, NUM:4, RPAREN, OP:*, NUM:2]` |
| **语法分析器** | token 列表 | AST（节点树） |
| **RPN 转换器** | AST 根节点 | `"3 4 + sin 2 *"` |
| **求值器** | RPN 字符串 | `1.31397` |
| **可视化器** | AST + 标签 | `.jpg` 图像 |

### 运算符优先级（定义于 `src/core/operators.py`）

| 符号 | 类型 | 优先级 | 结合性 |
|------|------|--------|--------|
| `+` `-` | 二元运算符 | 1 | 左结合 |
| `*` `/` | 二元运算符 | 2 | 左结合 |
| `^` | 二元运算符 | 3 | **右结合** |
| `sin` `cos` `tan` `log` | 一元函数 | 4（最高） | — |

`^` 的右结合性意味着 `2 ^ 3 ^ 2` 被解析为 `2 ^ (3 ^ 2)` = 512，而非 `(2 ^ 3) ^ 2` = 64。

> `log` 为**以 10 为底的对数**（常用对数，log₁₀）。`log(10) = 1`，`log(100) = 2`。**不是**自然对数（ln）。

---

## 支持的表达式

| 中缀表达式 | RPN | 结果 |
|-----------|-----|------|
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

### 复杂嵌套表达式

| 中缀表达式 | RPN | 结果 |
|-----------|-----|------|
| `sin(cos(1) + 2) * log(100)` | `1 cos 2 + sin 100 log *` | `1.13141` |
| `(sin(1) + cos(1)) ^ 2 + tan(1) * log(10)` | `1 sin 1 cos + 2 ^ 1 tan 10 log * +` | `3.46671` |
| `log(sin(1) * 10 + cos(1) * 10)` | `1 sin 10 * 1 cos 10 * + log` | `1.14044` |
| `sin(1 + cos(1)) * (log(100) + tan(1))` | `1 1 cos + sin 100 log 1 tan + *` | `3.55575` |
| `(sin(1) * cos(1) + log(10)) ^ 2` | `1 sin 1 cos * 10 log + 2 ^` | `2.11600` |
| `cos(sin(1) + tan(1)) * log(100) + sin(1) ^ 2` | `1 sin 1 tan + cos 100 log * 1 sin 2 ^ +` | `-0.76520` |
| `log(100) * (sin(1) + cos(1)) - tan(1) ^ 2` | `100 log 1 sin 1 cos + * 1 tan 2 ^ -` | `0.33803` |

---

## AST 可视化

每次计算都会在 `output/trees/` 目录生成一张 `.jpg` 图像。

图像包含三行标题：

```
sin(3 + 4) * 2          ← 原始中缀表达式
RPN:    3 4 + sin 2 *   ← 逆波兰表达式
Result: 1.31397         ← 计算结果
──────────────────────────────
         [AST 树形图]
```

- **橙色圆角矩形** — 运算符与函数（内部节点）
- **蓝色圆形** — 数字（叶子节点）
- **箭头** — 从父节点指向子节点

### 示例：`sin(3 + 4) * 2`

```
           *
          / \
        sin   2
         |
         +
        / \
       3   4
```

树结构编码了运算顺序：要计算 `*`，需要先算 `sin`；要算 `sin`，需要先算 `+`；`+` 需要 `3` 和 `4`。对该树做后序遍历，直接得到 RPN 字符串。

---

## 安装

```bash
git clone https://github.com/<you>/Reverse-Polish-Notation-Calculator.git
cd Reverse-Polish-Notation-Calculator
pip install -r requirements.txt
```

---

## 使用方法

### 交互式 REPL

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

### 单条表达式

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

也可以单独调用各个阶段：

```python
from src.core.parser        import parse
from src.core.rpn_converter import ast_to_rpn
from src.core.evaluator     import evaluate_rpn
from src.ast_tree.visualizer import render_ast

ast    = parse("2 ^ 3 ^ 2")
rpn    = ast_to_rpn(ast)          # "2 3 2 ^ ^"
result = evaluate_rpn(rpn)        # 512.0
render_ast(ast, "2 ^ 3 ^ 2", rpn, "output/trees/power.jpg", result=result)
```

---

## 运行测试

```bash
# 运行全套测试并输出覆盖率报告
python -m pytest tests/ -v

# 单个模块
python -m pytest tests/test_rpn_converter.py -v
```

共 107 个测试，覆盖词法分析器、语法分析器、RPN 转换器、求值器和可视化器全部模块。

---

## 项目结构

```
src/
├── core/
│   ├── operators.py       ← 唯一权威来源：优先级与结合性定义
│   ├── tokenizer.py       ← 字符串 → token 列表
│   ├── parser.py          ← token 列表 → AST（Pratt 递归下降）
│   ├── rpn_converter.py   ← AST → RPN 字符串（后序遍历）
│   └── evaluator.py       ← RPN 字符串 → 浮点数（栈机求值）
├── ast_tree/
│   ├── nodes.py           ← NumberNode / OperatorNode / FunctionNode
│   └── visualizer.py      ← AST → JPG（matplotlib）
└── ui/
    └── calculator.py      ← CLI 入口

tests/
├── test_operators.py
├── test_tokenizer.py
├── test_parser.py
├── test_rpn_converter.py
├── test_evaluator.py
└── test_visualizer.py

output/
└── trees/                 ← 生成的 JPG 图像（每条表达式一张）
```

---

## 错误处理

| 输入 | 错误 |
|------|------|
| `3 @ 4` | `ValueError: Unexpected character '@'` |
| `exp(1)` | `ValueError: Unknown function 'exp'` |
| `(3 + 4` | `ValueError: Expected RPAREN` |
| `5 / 0` | `ZeroDivisionError: Division by zero` |
| `3 +` | `ValueError: Malformed RPN` |
