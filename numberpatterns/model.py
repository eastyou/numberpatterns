"""数列规律识别与生成的核心模型。

本模块只依赖 Python 标准库，兼容 Python 3.9 及以上版本。
所有对外函数都会对输入做类型与取值校验：类型错误抛 ``TypeError``，
取值错误抛 ``ValueError``，错误消息统一使用中文。
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence as _SequenceABC
from typing import Callable, Dict, List, Optional, Tuple

__all__ = [
    "RULE_ORDER",
    "RULE_LABELS",
    "detect",
    "candidates",
    "next_term",
    "extend",
    "generate",
    "quiz_items",
]

#: 单个数列元素的绝对值上限。
MAX_ABS_VALUE: int = 1_000_000

#: 识别规律时允许的最短长度（斐波那契型允许 3 项）。
MIN_TERMS: int = 3

#: 规律优先级：从简到繁，越靠前越优先。
RULE_ORDER: Tuple[str, ...] = (
    "constant",
    "arithmetic",
    "geometric",
    "squares",
    "fibonacci",
    "alternating",
    "quadratic",
)

#: 规律名称到中文标签的映射。
RULE_LABELS: Dict[str, str] = {
    "constant": "常数数列",
    "arithmetic": "等差数列",
    "geometric": "等比数列",
    "squares": "平方数列",
    "fibonacci": "斐波那契型数列",
    "alternating": "交替数列",
    "quadratic": "二阶差分数列",
}

#: 难度等级到可用规律的映射。
_LEVEL_RULES: Dict[str, Tuple[str, ...]] = {
    "easy": ("constant", "arithmetic", "geometric"),
    "normal": (
        "constant",
        "arithmetic",
        "geometric",
        "squares",
        "fibonacci",
    ),
    "hard": RULE_ORDER,
}

#: 单条规律识别结果（内部使用，额外携带 data 字段）。
_RuleInfo = Dict[str, object]

_Matcher = Callable[[List[int]], Optional[_RuleInfo]]


def _is_int(value: object) -> bool:
    """判断是否为整数且不是布尔值。"""
    return isinstance(value, int) and not isinstance(value, bool)


def _as_int(value: object) -> int:
    """把内部规律参数转换为整数，失败时抛出中文 TypeError。"""
    if not _is_int(value):
        raise TypeError("内部错误：规律参数不是整数")
    return value


def _validate_terms(terms: Sequence[int]) -> List[int]:
    """校验数列输入并返回列表副本。

    空数列、长度不足、非整数元素、数值越界都会抛出中文异常。
    """
    if isinstance(terms, (str, bytes, bytearray)) or not isinstance(
        terms, _SequenceABC
    ):
        raise TypeError("数列必须是整数序列（list 或 tuple）")
    values = list(terms)
    if not values:
        raise ValueError("数列不能为空")
    if len(values) < MIN_TERMS:
        raise ValueError("数列长度不足，至少需要 3 项")
    for index, item in enumerate(values):
        if not _is_int(item):
            raise TypeError("数列第 %d 项必须是整数" % (index + 1))
        if abs(item) > MAX_ABS_VALUE:
            raise ValueError(
                "数列第 %d 项的绝对值超过 %d" % (index + 1, MAX_ABS_VALUE)
            )
    return values


def _validate_count(count: int, minimum: int, maximum: int, label: str) -> int:
    """校验数量类参数。"""
    if not _is_int(count):
        raise TypeError("%s必须是整数" % label)
    if count < minimum or count > maximum:
        raise ValueError(
            "%s必须在 %d 到 %d 之间" % (label, minimum, maximum)
        )
    return count


def _square_root(value: int) -> Optional[int]:
    """返回完全平方数的非负平方根，否则返回 None。"""
    if value < 0:
        return None
    root = math.isqrt(value)
    if root * root == value:
        return root
    return None


def _match_constant(values: List[int]) -> Optional[_RuleInfo]:
    """常数数列：每一项都相同。"""
    first = values[0]
    for item in values:
        if item != first:
            return None
    return {
        "rule": "constant",
        "next": first,
        "detail": "常数数列：每一项都是 %d。" % first,
        "data": {"value": first},
    }


def _match_arithmetic(values: List[int]) -> Optional[_RuleInfo]:
    """等差数列：相邻两项之差恒定。"""
    diff = values[1] - values[0]
    for index in range(len(values) - 1):
        if values[index + 1] - values[index] != diff:
            return None
    return {
        "rule": "arithmetic",
        "next": values[-1] + diff,
        "detail": "等差数列：公差为 %d。" % diff,
        "data": {"diff": diff},
    }


def _match_geometric(values: List[int]) -> Optional[_RuleInfo]:
    """等比数列：相邻两项之比为整数，且公比不等于 0 或 1。"""
    if values[0] == 0:
        return None
    if values[1] % values[0] != 0:
        return None
    ratio = values[1] // values[0]
    if ratio in (0, 1):
        return None
    for index in range(len(values) - 1):
        if values[index] * ratio != values[index + 1]:
            return None
    return {
        "rule": "geometric",
        "next": values[-1] * ratio,
        "detail": "等比数列：公比为 %d。" % ratio,
        "data": {"ratio": ratio},
    }


def _match_squares(values: List[int]) -> Optional[_RuleInfo]:
    """平方数列：连续整数的平方，允许起点偏移。"""
    root = _square_root(values[0])
    if root is None:
        return None
    for index, item in enumerate(values):
        current = _square_root(item)
        if current is None or current != root + index:
            return None
    next_root = root + len(values)
    return {
        "rule": "squares",
        "next": next_root * next_root,
        "detail": "平方数列：从 %d² 开始，依次为连续整数的平方。" % root,
        "data": {"root": root},
    }


def _match_fibonacci(values: List[int]) -> Optional[_RuleInfo]:
    """斐波那契型：从第 3 项起，每项等于前两项之和。"""
    if len(values) < 3:
        return None
    for index in range(2, len(values)):
        if values[index] != values[index - 1] + values[index - 2]:
            return None
    return {
        "rule": "fibonacci",
        "next": values[-1] + values[-2],
        "detail": "斐波那契型数列：从第 3 项起，每一项等于前两项之和。",
        "data": {},
    }


def _match_alternating(values: List[int]) -> Optional[_RuleInfo]:
    """交替数列：奇数位与偶数位各自等差，且公差相同。"""
    if len(values) < 4:
        return None
    diffs = [values[index + 1] - values[index] for index in range(len(values) - 1)]
    if len(set(diffs)) == 1:
        # 纯等差数列（含常数数列）由更高优先级的规律负责。
        return None
    diff = values[2] - values[0]
    if diff == 0:
        return None
    for index in range(len(values) - 2):
        if values[index + 2] - values[index] != diff:
            return None
    return {
        "rule": "alternating",
        "next": values[-2] + diff,
        "detail": "交替数列：奇数位与偶数位各自等差，公差为 %d。" % diff,
        "data": {"diff": diff},
    }


def _match_quadratic(values: List[int]) -> Optional[_RuleInfo]:
    """二阶差分数列：二阶差分恒定且不为 0。"""
    if len(values) < 4:
        return None
    diffs = [values[index + 1] - values[index] for index in range(len(values) - 1)]
    second = diffs[1] - diffs[0]
    if second == 0:
        return None
    for index in range(len(diffs) - 1):
        if diffs[index + 1] - diffs[index] != second:
            return None
    next_diff = diffs[-1] + second
    return {
        "rule": "quadratic",
        "next": values[-1] + next_diff,
        "detail": "二阶差分数列：二阶差分恒为 %d。" % second,
        "data": {"last_diff": diffs[-1], "second_diff": second},
    }


_MATCHERS: Tuple[Tuple[str, _Matcher], ...] = (
    ("constant", _match_constant),
    ("arithmetic", _match_arithmetic),
    ("geometric", _match_geometric),
    ("squares", _match_squares),
    ("fibonacci", _match_fibonacci),
    ("alternating", _match_alternating),
    ("quadratic", _match_quadratic),
)


def _matches(values: List[int]) -> List[_RuleInfo]:
    """按优先级返回所有成立的规律。"""
    result: List[_RuleInfo] = []
    for _name, matcher in _MATCHERS:
        info = matcher(values)
        if info is not None:
            result.append(info)
    return result


def _analyze(values: List[int]) -> List[_RuleInfo]:
    """返回全部成立规律，并处理长度不足的特殊情况。"""
    if len(values) < 4:
        fibonacci = _match_fibonacci(values)
        if fibonacci is None:
            raise ValueError("数列长度不足，至少需要 4 项才能识别规律")
        return [fibonacci]
    matches = _matches(values)
    if not matches:
        raise ValueError("无法识别该数列的规律")
    return matches


def _public(info: _RuleInfo) -> Dict[str, object]:
    """去掉内部 data 字段，返回公共结果。"""
    return {
        "rule": info["rule"],
        "next": info["next"],
        "detail": info["detail"],
    }


def detect(terms: Sequence[int]) -> Dict[str, object]:
    """识别数列规律，返回 ``{"rule", "next", "detail"}``。

    长度至少 4 项（斐波那契型允许 3 项）。当多条规律同时成立时，
    按 :data:`RULE_ORDER` 的优先级取第一条，并在说明中注明。
    """
    values = _validate_terms(terms)
    matches = _analyze(values)
    first = matches[0]
    detail = str(first["detail"])
    if len(matches) > 1:
        others = "、".join(
            RULE_LABELS.get(str(info["rule"]), str(info["rule"]))
            for info in matches[1:]
        )
        detail = "%s（同时满足：%s，按优先级取前者）" % (detail, others)
    return {
        "rule": first["rule"],
        "next": first["next"],
        "detail": detail,
    }


def candidates(terms: Sequence[int]) -> List[Dict[str, object]]:
    """返回所有成立规律及各自下一项，用于课堂讨论“答案可能不唯一”。

    无规律时抛出中文 ``ValueError``；长度要求与 :func:`detect` 一致。
    """
    values = _validate_terms(terms)
    return [_public(info) for info in _analyze(values)]


def next_term(terms: Sequence[int]) -> int:
    """按优先级最高的规律预测下一项。"""
    info = detect(terms)
    return _as_int(info["next"])


def _advance(rule: str, values: List[int], data: Dict[str, object]) -> int:
    """根据已识别的规律推进一步，必要时更新内部参数。"""
    if rule == "constant":
        return values[-1]
    if rule == "arithmetic":
        return values[-1] + _as_int(data["diff"])
    if rule == "geometric":
        return values[-1] * _as_int(data["ratio"])
    if rule == "squares":
        root = _as_int(data["root"])
        next_root = root + len(values)
        return next_root * next_root
    if rule == "fibonacci":
        return values[-1] + values[-2]
    if rule == "alternating":
        return values[-2] + _as_int(data["diff"])
    if rule == "quadratic":
        last_diff = _as_int(data["last_diff"])
        second_diff = _as_int(data["second_diff"])
        next_diff = last_diff + second_diff
        data["last_diff"] = next_diff
        return values[-1] + next_diff
    raise ValueError("未知规律：%s" % rule)


def extend(terms: Sequence[int], count: int) -> List[int]:
    """按识别出的规律向后扩展 ``count`` 项，返回包含原数列的完整序列。"""
    _validate_count(count, 1, 20, "扩展项数")
    values = _validate_terms(terms)
    first = _analyze(values)[0]
    rule = str(first["rule"])
    data = first["data"]
    if not isinstance(data, dict):
        raise TypeError("内部错误：规律数据格式无效")
    working = list(values)
    for _step in range(count):
        working.append(_advance(rule, working, data))
    return working


def _make_rng(seed: Optional[int]) -> random.Random:
    """创建随机数生成器，种子必须是整数或 None。"""
    if seed is not None and not _is_int(seed):
        raise TypeError("随机种子必须是整数或 None")
    return random.Random(seed)


def _check_generated(values: List[int]) -> List[int]:
    """检查生成结果是否在允许的数值范围内。"""
    for index, item in enumerate(values):
        if abs(item) > MAX_ABS_VALUE:
            raise ValueError(
                "生成的第 %d 项超出范围（±%d），请减小起始值或项数"
                % (index + 1, MAX_ABS_VALUE)
            )
    return values


def generate(
    rule: str,
    start: int,
    count: int,
    seed: Optional[int] = None,
) -> List[int]:
    """按指定规律生成数列。

    ``start`` 对大多数规律表示首项；对 ``squares`` 表示起始平方根
    （例如 ``start=2`` 生成 4, 9, 16, 25）。``count`` 必须在 4 到 12 之间。
    """
    if not isinstance(rule, str):
        raise TypeError("规律名称必须是字符串")
    if rule not in RULE_ORDER:
        raise ValueError("未知规律：%s" % rule)
    if not _is_int(start):
        raise TypeError("起始值必须是整数")
    if abs(start) > MAX_ABS_VALUE:
        raise ValueError("起始值超出范围（±%d）" % MAX_ABS_VALUE)
    _validate_count(count, 4, 12, "生成项数")
    rng = _make_rng(seed)

    if rule == "constant":
        values = [start] * count
    elif rule == "arithmetic":
        step = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4, 5])
        values = [start + step * index for index in range(count)]
    elif rule == "geometric":
        if start == 0:
            raise ValueError("等比数列的起始项不能为 0")
        ratio = rng.choice([-3, -2, 2, 3])
        values = [start * (ratio ** index) for index in range(count)]
    elif rule == "squares":
        if start < 0:
            raise ValueError("平方数列的起始根不能为负数")
        values = [(start + index) ** 2 for index in range(count)]
    elif rule == "fibonacci":
        second = start + rng.choice([1, 2, 3, 4, 5])
        values = [start, second]
        while len(values) < count:
            values.append(values[-1] + values[-2])
    elif rule == "alternating":
        diff = rng.choice([1, 2, 3, 4, 5])
        offset = rng.choice([2, 3, 4, 5, 6])
        if 2 * offset == diff:
            offset += 1
        values = []
        for index in range(count):
            base = start if index % 2 == 0 else start + offset
            values.append(base + (index // 2) * diff)
    elif rule == "quadratic":
        first_diff = rng.choice([1, 2, 3, 4, 5])
        second_diff = rng.choice([1, 2, 3])
        if second_diff == 2 and first_diff % 2 == 1:
            # 避免与平方数列重合，保证优先识别为二阶差分数列。
            second_diff = 3
        values = [start]
        diff = first_diff
        for _index in range(count - 1):
            values.append(values[-1] + diff)
            diff += second_diff
    else:  # pragma: no cover - 上面的分支已覆盖 RULE_ORDER
        raise ValueError("未知规律：%s" % rule)

    return _check_generated(values)


def _random_start(rule: str, rng: random.Random) -> int:
    """为练习题随机选择起始值。"""
    if rule == "squares":
        return rng.randint(0, 6)
    if rule == "geometric":
        return rng.choice([-3, -2, -1, 1, 2, 3])
    return rng.randint(-5, 9)


def _build_terms(
    rule: str,
    start: int,
    length: int,
    rng: random.Random,
) -> List[int]:
    """按规律构造指定长度的数列（练习题使用）。"""
    if rule == "constant":
        return [start] * length
    if rule == "arithmetic":
        step = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4, 5])
        return [start + step * index for index in range(length)]
    if rule == "geometric":
        ratio = rng.choice([-3, -2, 2, 3])
        return [start * (ratio ** index) for index in range(length)]
    if rule == "squares":
        return [(start + index) ** 2 for index in range(length)]
    if rule == "fibonacci":
        second = start + rng.choice([1, 2, 3, 4])
        values = [start, second]
        while len(values) < length:
            values.append(values[-1] + values[-2])
        return values
    if rule == "alternating":
        diff = rng.choice([1, 2, 3, 4, 5])
        offset = rng.choice([2, 3, 4, 5, 6])
        if 2 * offset == diff:
            offset += 1
        values = []
        for index in range(length):
            base = start if index % 2 == 0 else start + offset
            values.append(base + (index // 2) * diff)
        return values
    first_diff = rng.choice([1, 2, 3, 4, 5])
    second_diff = rng.choice([1, 2, 3])
    if second_diff == 2 and first_diff % 2 == 1:
        second_diff = 3
    values = [start]
    diff = first_diff
    for _index in range(length - 1):
        values.append(values[-1] + diff)
        diff += second_diff
    return values


def _make_quiz_item(
    rng: random.Random,
    pool: Tuple[str, ...],
) -> Dict[str, object]:
    """生成一道练习题，保证答案与识别出的规律一致。"""
    for _attempt in range(60):
        rule = rng.choice(pool)
        length = rng.choice([4, 5])
        start = _random_start(rule, rng)
        terms = _build_terms(rule, start, length, rng)
        try:
            info = detect(terms)
        except (TypeError, ValueError):
            continue
        if str(info["rule"]) not in pool:
            continue
        return {
            "terms": terms,
            "answer": info["next"],
            "rule": info["rule"],
            "detail": info["detail"],
        }

    # 兜底：等差数列在所有难度等级中都存在。
    start = rng.randint(-5, 9)
    step = rng.choice([1, 2, 3, 4, 5])
    terms = [start + step * index for index in range(5)]
    info = detect(terms)
    return {
        "terms": terms,
        "answer": info["next"],
        "rule": info["rule"],
        "detail": info["detail"],
    }


def quiz_items(
    count: int,
    seed: Optional[int] = None,
    level: str = "normal",
) -> List[Dict[str, object]]:
    """生成练习题列表。

    每题包含 ``terms``（4~5 项）、``answer``、``rule``、``detail``。
    ``level`` 仅接受 ``easy``、``normal``、``hard``；``count`` 为 1~30。
    """
    if not isinstance(level, str):
        raise TypeError("难度等级必须是字符串")
    if level not in _LEVEL_RULES:
        raise ValueError("难度等级必须是 easy、normal 或 hard")
    _validate_count(count, 1, 30, "题目数量")
    rng = _make_rng(seed)
    pool = _LEVEL_RULES[level]
    items: List[Dict[str, object]] = []
    for _index in range(count):
        items.append(_make_quiz_item(rng, pool))
    return items
