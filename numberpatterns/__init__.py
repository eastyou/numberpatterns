"""numberpatterns：数列规律识别、预测与练习页生成。

公共 API 全部从本包顶层导出，方便直接 ``from numberpatterns import detect``。
"""

from __future__ import annotations

from .model import (
    RULE_LABELS,
    RULE_ORDER,
    candidates,
    detect,
    extend,
    generate,
    next_term,
    quiz_items,
)
from .render import LEVEL_LABELS, poster_html, quiz_html

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "RULE_ORDER",
    "RULE_LABELS",
    "LEVEL_LABELS",
    "detect",
    "candidates",
    "next_term",
    "extend",
    "generate",
    "quiz_items",
    "quiz_html",
    "poster_html",
]
