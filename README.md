# numberpatterns · 数列规律

[![CI](https://github.com/eastyou/numberpatterns/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/numberpatterns/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

面向师生的 Python 标准库小工具：**识别数列规律、预测下一项、生成可打印练习页**。
零第三方依赖，同时兼容 Python 3.9 与 3.15，适合课堂演示、随堂练习与课后打印。

## 特性

- 支持 7 类常见规律：常数、等差、等比、平方、斐波那契型、交替、二阶差分。
- 按「从简到繁」的固定优先级识别；多条规律同时成立时会明确提示。
- 既能预测下一项，也能列出全部可能规律，方便课堂讨论「答案为什么可能不唯一」。
- 一键生成 A4 打印练习页（题目横排 + 答案分页）与 7 类规律速查表。
- 所有输入都有中文校验提示；所有文件读写使用 UTF-8。
- 纯标准库实现，无任何第三方依赖。

## 规律与优先级

| 优先级 | 规律 | 识别特征 | 示例 | 下一项 |
| --- | --- | --- | --- | --- |
| 1 | 常数数列 | 每一项都相同 | `5, 5, 5, 5` | `5` |
| 2 | 等差数列 | 相邻两项之差相同 | `2, 4, 6, 8` | `10` |
| 3 | 等比数列 | 相邻两项之比为整数（≠ 0、1） | `1, 3, 9, 27` | `81` |
| 4 | 平方数列 | 连续整数的平方，允许起点偏移 | `1, 4, 9, 16` | `25` |
| 5 | 斐波那契型 | 从第 3 项起，每项等于前两项之和 | `1, 1, 2, 3, 5` | `8` |
| 6 | 交替数列 | 奇数位与偶数位各自等差且公差相同 | `1, 4, 2, 5, 3, 6` | `4` |
| 7 | 二阶差分数列 | 二阶差分恒定（不为 0） | `2, 5, 10, 17` | `26` |

> 例如 `1, 4, 9, 16` 同时满足平方数列与二阶差分数列，程序会按优先级选择平方数列，
> 并在 `detail` 中注明「同时满足：二阶差分数列」。

识别规则的长度要求：一般为 **至少 4 项**；斐波那契型允许 **3 项**。
数列元素必须是整数（布尔值不算），且绝对值不超过 `1_000_000`。

## 安装

需要 Python 3.9 或更高版本。

```bash
pip install .
```

开发模式安装：

```bash
pip install -e .
```

安装后可直接使用 `numberpatterns` 命令；不安装也可以在仓库根目录使用
`python -m numberpatterns`。

## 命令行用法

```bash
# 预测下一项
$ numberpatterns next 2 4 6 8
下一项：10

# 识别规律并查看说明
$ numberpatterns rule 1 4 9 16
规律：平方数列
说明：平方数列：从 1² 开始，依次为连续整数的平方。（同时满足：二阶差分数列，按优先级取前者）
下一项：25

# 列出所有成立的规律
$ numberpatterns candidates 1 4 9 16
共有 2 种成立的规律：
- 平方数列（下一项 25）：平方数列：从 1² 开始，依次为连续整数的平方。
- 二阶差分数列（下一项 25）：二阶差分数列：二阶差分恒为 2。

# 按规律向后扩展
$ numberpatterns extend 2 4 6 8 --count 3
扩展后：2 4 6 8 10 12 14

# 生成 10 道困难题（固定随机种子，结果可复现）
$ numberpatterns quiz --count 10 --seed 5 --level hard -o examples/quiz.html
已生成：examples/quiz.html

# 生成 7 类规律速查表
$ numberpatterns poster -o examples/poster.html
已生成：examples/poster.html
```

`quiz` 还支持 `--answers`，在练习题后附加单独一页参考答案。
省略 `-o` 时，HTML 会直接输出到终端，便于重定向到文件。

## 库用法

```python
from numberpatterns import (
    candidates,
    detect,
    extend,
    generate,
    next_term,
    quiz_html,
    quiz_items,
)

info = detect([1, 4, 9, 16])
print(info)
# {'rule': 'squares', 'next': 25, 'detail': '平方数列：从 1² 开始，……'}

print(next_term([2, 5, 10, 17]))   # 26
print(extend([2, 4, 6, 8], 3))     # [2, 4, 6, 8, 10, 12, 14]

print([item["rule"] for item in candidates([1, 4, 9, 16])])
# ['squares', 'quadratic']

print(generate("geometric", 2, 5, seed=1))
# [2, -4, 8, -16, 32]

items = quiz_items(10, seed=5, level="hard")
html_text = quiz_html(items, "数列规律练习", with_answers=True)
with open("quiz.html", "w", encoding="utf-8") as handle:
    handle.write(html_text)
```

### 公共 API

| 函数 | 说明 |
| --- | --- |
| `detect(terms)` | 返回 `{"rule", "next", "detail"}`，按优先级选取唯一规律 |
| `candidates(terms)` | 返回所有成立规律及各自下一项 |
| `next_term(terms)` | 返回下一项 |
| `extend(terms, count)` | 向后扩展 1~20 项，返回含原数列的完整列表 |
| `generate(rule, start, count, seed=None)` | 按指定规律生成 4~12 项 |
| `quiz_items(count, seed=None, level="normal")` | 生成 1~30 道练习题 |
| `quiz_html(items, title, with_answers=False, level="normal")` | 渲染练习页 HTML |
| `poster_html()` | 渲染 7 类规律速查表 |

难度等级：

- `easy`：常数、等差、等比；
- `normal`：在 `easy` 基础上增加平方、斐波那契型；
- `hard`：全部 7 类规律。

## 示例文件

- [`examples/quiz.html`](examples/quiz.html)：10 道困难题练习页（题目 + 打印样式）；
- [`examples/poster.html`](examples/poster.html)：7 类规律速查表。

两个文件均可直接用浏览器打开，并通过浏览器打印为 A4 PDF。

## 目录结构

```text
numberpatterns/
├── __init__.py          # 公共 API 与 __version__
├── __main__.py          # python -m numberpatterns 入口
├── model.py             # 规律识别、预测、生成与出题
├── render.py            # 练习页与速查表 HTML 渲染
├── cli.py               # 命令行接口
├── tests/               # unittest 单元测试
├── examples/            # 生成好的示例 HTML
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
└── .github/workflows/ci.yml
```

## 测试

全部测试使用标准库 `unittest`，共 **155** 个测试：

```bash
python -m unittest discover -s tests -v
```

CI 在 Ubuntu、Windows、macOS 三个系统上运行，覆盖 Python 3.9 / 3.10 / 3.13。

## 兼容性

- 仅使用 Python 3.9+ 标准库；
- 不使用 `X | None`、`match`、海象运算符等 3.10+ 语法；
- 所有公开函数均带完整类型注解；
- 对外部输入统一做类型与取值校验，错误消息为中文。

## 许可证

MIT © 2026 eastyou
