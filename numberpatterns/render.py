"""把练习题和速查表渲染为可打印的 HTML。

所有动态文本都会经过 HTML 转义，页面自带 A4 打印样式。
"""

from __future__ import annotations

import html
from collections.abc import Sequence as _SequenceABC
from typing import Dict, List

from .model import RULE_LABELS

__all__ = ["quiz_html", "poster_html", "LEVEL_LABELS"]

#: 难度等级到中文标签的映射。
LEVEL_LABELS: Dict[str, str] = {
    "easy": "简单",
    "normal": "普通",
    "hard": "困难",
}

_BASE_STYLE = """
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 24px;
    background: #eef2f7;
    color: #1f2937;
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
        "Noto Sans CJK SC", sans-serif;
    line-height: 1.6;
}
.sheet {
    max-width: 820px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 14px;
    padding: 32px 36px 40px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}
h1 { margin: 0 0 6px; font-size: 26px; letter-spacing: 1px; }
.meta { margin: 0 0 24px; color: #64748b; font-size: 14px; }
.mono { font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; }
@page { size: A4; margin: 14mm; }
@media print {
    body { background: #ffffff; padding: 0; }
    .sheet { box-shadow: none; border-radius: 0; max-width: none; padding: 0; }
    .answers { break-before: page; page-break-before: always; }
    .question, .rule-card { break-inside: avoid; page-break-inside: avoid; }
}
"""

_QUIZ_STYLE = """
.grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}
.question {
    display: flex;
    gap: 12px;
    border: 1px solid #dbe3ee;
    border-radius: 10px;
    padding: 14px 16px;
    background: #f8fafc;
}
.q-no {
    flex: 0 0 30px;
    height: 30px;
    border-radius: 50%;
    background: #2563eb;
    color: #ffffff;
    font-size: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.q-body { flex: 1 1 auto; }
.q-terms { font-size: 19px; font-weight: 600; letter-spacing: 0.5px; }
.blank {
    display: inline-block;
    min-width: 44px;
    border-bottom: 2px solid #2563eb;
    text-align: center;
    color: #2563eb;
}
.q-line { margin-top: 10px; height: 1px; background: #cbd5e1; }
.answers { margin-top: 36px; }
.answers h2 { font-size: 20px; border-left: 4px solid #2563eb; padding-left: 10px; }
.answers ol { padding-left: 20px; }
.answers li { margin: 10px 0; }
.ans-value {
    display: inline-block;
    min-width: 54px;
    font-weight: 700;
    color: #b91c1c;
    font-family: "SFMono-Regular", Consolas, monospace;
}
.ans-rule { color: #2563eb; margin-right: 8px; }
.ans-detail { color: #64748b; font-size: 14px; }
@media (max-width: 640px) {
    .grid { grid-template-columns: 1fr; }
}
@media print {
    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
"""

_POSTER_STYLE = """
table { width: 100%; border-collapse: collapse; margin-top: 18px; }
th, td { border: 1px solid #cbd5e1; padding: 10px 12px; text-align: left; }
thead th { background: #eff6ff; color: #1d4ed8; }
tbody th { background: #f8fafc; white-space: nowrap; }
.rule-card { margin-top: 22px; padding: 14px 18px; background: #f8fafc;
    border-left: 4px solid #2563eb; border-radius: 8px; }
.rule-card h2 { margin: 0 0 6px; font-size: 17px; }
.rule-card p { margin: 4px 0; font-size: 14px; color: #475569; }
@media (max-width: 640px) {
    table, thead, tbody, th, td, tr { display: block; }
    thead { display: none; }
    tr { margin-bottom: 12px; border: 1px solid #cbd5e1; border-radius: 8px; }
    th, td { border: none; border-bottom: 1px dashed #e2e8f0; }
}
"""


def _escape(value: object) -> str:
    """把任意值转成经过 HTML 转义的字符串。"""
    return html.escape(str(value), quote=True)


def _validate_items(
    items: Sequence[Dict[str, object]],
) -> List[Dict[str, object]]:
    """校验题目列表，返回规范化后的副本。"""
    if isinstance(items, (str, bytes, bytearray)) or not isinstance(
        items, _SequenceABC
    ):
        raise TypeError("题目列表必须是序列")
    result: List[Dict[str, object]] = []
    for index, item in enumerate(items):
        position = index + 1
        if not isinstance(item, dict):
            raise TypeError("第 %d 道题必须是字典" % position)
        for key in ("terms", "answer", "rule", "detail"):
            if key not in item:
                raise ValueError("第 %d 道题缺少字段：%s" % (position, key))
        terms = item["terms"]
        if isinstance(terms, (str, bytes, bytearray)) or not isinstance(
            terms, _SequenceABC
        ):
            raise TypeError("第 %d 道题的 terms 必须是整数序列" % position)
        normalized_terms: List[int] = []
        if len(terms) == 0:
            raise ValueError("第 %d 道题的 terms 不能为空" % position)
        for term in terms:
            if not isinstance(term, int) or isinstance(term, bool):
                raise TypeError("第 %d 道题的 terms 必须全部是整数" % position)
            normalized_terms.append(term)
        answer = item["answer"]
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise TypeError("第 %d 道题的 answer 必须是整数" % position)
        rule = item["rule"]
        if not isinstance(rule, str) or rule == "":
            raise TypeError("第 %d 道题的 rule 必须是非空字符串" % position)
        detail = item["detail"]
        if not isinstance(detail, str):
            raise TypeError("第 %d 道题的 detail 必须是字符串" % position)
        result.append(
            {
                "terms": normalized_terms,
                "answer": answer,
                "rule": rule,
                "detail": detail,
            }
        )
    return result


def _question_cards(items: List[Dict[str, object]]) -> str:
    """渲染题目卡片。"""
    cards: List[str] = []
    for index, item in enumerate(items):
        terms = item["terms"]
        if not isinstance(terms, list):
            continue
        terms_text = ", ".join(str(term) for term in terms)
        cards.append(
            '<section class="question">'
            '<div class="q-no">%d</div>'
            '<div class="q-body">'
            '<div class="q-terms mono">%s, <span class="blank">?</span></div>'
            '<div class="q-line"></div>'
            "</div>"
            "</section>" % (index + 1, _escape(terms_text))
        )
    return "\n".join(cards)


def _answer_list(items: List[Dict[str, object]]) -> str:
    """渲染答案页列表。"""
    entries: List[str] = []
    for index, item in enumerate(items):
        rule = str(item["rule"])
        label = RULE_LABELS.get(rule, rule)
        entries.append(
            "<li>"
            '<span class="ans-value">%s</span>'
            '<span class="ans-rule">%s</span>'
            '<span class="ans-detail">%s</span>'
            "</li>"
            % (
                _escape(item["answer"]),
                _escape(label),
                _escape(item["detail"]),
            )
        )
    return "\n".join(entries)


def quiz_html(
    items: Sequence[Dict[str, object]],
    title: str,
    with_answers: bool = False,
    level: str = "normal",
) -> str:
    """把练习题渲染为可打印的 HTML 字符串。

    ``with_answers`` 为 True 时，在单独一页附上参考答案。
    """
    if not isinstance(title, str):
        raise TypeError("标题必须是字符串")
    if not isinstance(with_answers, bool):
        raise TypeError("答案开关必须是布尔值")
    if not isinstance(level, str):
        raise TypeError("难度等级必须是字符串")
    if level not in LEVEL_LABELS:
        raise ValueError("难度等级必须是 easy、normal 或 hard")

    rows = _validate_items(items)
    cards = _question_cards(rows)
    answers = ""
    if with_answers:
        answers = (
            '<section class="answers">'
            "<h2>参考答案</h2>"
            "<ol>%s</ol>"
            "</section>" % _answer_list(rows)
        )

    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n"
        "<style>%s%s</style>\n"
        "</head>\n"
        "<body>\n"
        '<main class="sheet">\n'
        "<h1>%s</h1>\n"
        '<p class="meta">难度：%s &middot; 共 %d 题 &middot; '
        "姓名：________ &nbsp; 日期：________</p>\n"
        '<div class="grid">\n%s\n</div>\n'
        "%s\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
        % (
            _escape(title),
            _BASE_STYLE,
            _QUIZ_STYLE,
            _escape(title),
            _escape(LEVEL_LABELS[level]),
            len(rows),
            cards,
            answers,
        )
    )


#: 速查表内容：(规律名称, 识别特征, 示例, 下一项)。
_POSTER_ROWS = (
    ("constant", "每一项都相同", "5, 5, 5, 5", "5"),
    ("arithmetic", "相邻两项之差相同", "2, 4, 6, 8", "10"),
    ("geometric", "相邻两项之比为整数（≠ 0、1）", "1, 3, 9, 27", "81"),
    ("squares", "连续整数的平方，可偏移起点", "1, 4, 9, 16", "25"),
    ("fibonacci", "从第 3 项起，每项等于前两项之和", "1, 1, 2, 3, 5", "8"),
    ("alternating", "奇数位与偶数位各自等差且公差相同", "1, 4, 2, 5, 3, 6", "4"),
    ("quadratic", "二阶差分恒定（不为 0）", "2, 5, 10, 17", "26"),
)


def poster_html() -> str:
    """渲染 7 类数列规律的速查表（A4 可打印）。"""
    rows_html: List[str] = []
    cards_html: List[str] = []
    for rule, feature, example, nxt in _POSTER_ROWS:
        label = RULE_LABELS.get(rule, rule)
        rows_html.append(
            "<tr>"
            "<th>%s</th>"
            "<td>%s</td>"
            '<td class="mono">%s</td>'
            '<td class="mono">%s</td>'
            "</tr>"
            % (
                _escape(label),
                _escape(feature),
                _escape(example),
                _escape(nxt),
            )
        )
        cards_html.append(
            '<section class="rule-card">'
            "<h2>%s</h2>"
            "<p>识别：%s</p>"
            '<p class="mono">示例：%s → %s</p>'
            "</section>"
            % (
                _escape(label),
                _escape(feature),
                _escape(example),
                _escape(nxt),
            )
        )

    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>数列规律速查表</title>\n"
        "<style>%s%s</style>\n"
        "</head>\n"
        "<body>\n"
        '<main class="sheet">\n'
        "<h1>数列规律速查表</h1>\n"
        '<p class="meta">7 类常见规律 &middot; 按优先级从简到繁排列</p>\n'
        "<table>\n"
        "<thead><tr><th>规律</th><th>识别特征</th>"
        "<th>示例</th><th>下一项</th></tr></thead>\n"
        "<tbody>\n%s\n</tbody>\n"
        "</table>\n"
        "%s\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
        % (
            _BASE_STYLE,
            _POSTER_STYLE,
            "\n".join(rows_html),
            "\n".join(cards_html),
        )
    )
