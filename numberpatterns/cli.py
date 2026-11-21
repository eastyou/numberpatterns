"""命令行入口：识别规律、扩展数列、生成练习页与速查表。"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence as _SequenceABC
from typing import Callable, List, Optional, Sequence

from . import model, render
from .model import RULE_LABELS

__all__ = ["main"]

_Handler = Callable[[argparse.Namespace], int]


def _ensure_utf8_console() -> None:
    """尽量把标准输出与标准错误切换为 UTF-8，避免 Windows 乱码。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def _parse_terms(raw: Sequence[str]) -> List[int]:
    """把命令行中的字符串数值解析为整数列表。"""
    if isinstance(raw, (str, bytes, bytearray)) or not isinstance(
        raw, _SequenceABC
    ):
        raise TypeError("数值列表格式无效")
    values: List[int] = []
    for index, token in enumerate(raw):
        if not isinstance(token, str):
            raise TypeError("第 %d 个数值必须是字符串" % (index + 1))
        try:
            values.append(int(token.strip(), 10))
        except ValueError:
            raise ValueError("数值格式错误：%s" % token) from None
    return values


def _parse_int(value: str, label: str) -> int:
    """解析单个整数参数，失败时抛出中文 ValueError。"""
    try:
        return int(str(value).strip(), 10)
    except (TypeError, ValueError):
        raise ValueError("%s必须是整数：%s" % (label, value)) from None


def _write_file(path: str, content: str) -> None:
    """以 UTF-8 写入文件，OSError 转换为中文 ValueError。"""
    if not isinstance(path, str) or path.strip() == "":
        raise TypeError("输出路径必须是非空字符串")
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError("无法写入文件 %s：%s" % (path, exc)) from exc


def _emit(content: str, output: Optional[str]) -> int:
    """把内容打印到终端或写入文件。"""
    if output is None:
        print(content)
        return 0
    _write_file(output, content)
    print("已生成：%s" % output)
    return 0


def _cmd_next(args: argparse.Namespace) -> int:
    terms = _parse_terms(args.numbers)
    print("下一项：%d" % model.next_term(terms))
    return 0


def _cmd_rule(args: argparse.Namespace) -> int:
    terms = _parse_terms(args.numbers)
    info = model.detect(terms)
    label = RULE_LABELS.get(str(info["rule"]), str(info["rule"]))
    print("规律：%s" % label)
    print("说明：%s" % info["detail"])
    print("下一项：%d" % info["next"])
    return 0


def _cmd_candidates(args: argparse.Namespace) -> int:
    terms = _parse_terms(args.numbers)
    results = model.candidates(terms)
    print("共有 %d 种成立的规律：" % len(results))
    for info in results:
        label = RULE_LABELS.get(str(info["rule"]), str(info["rule"]))
        print("- %s（下一项 %d）：%s" % (label, info["next"], info["detail"]))
    return 0


def _cmd_extend(args: argparse.Namespace) -> int:
    terms = _parse_terms(args.numbers)
    count = _parse_int(args.count, "扩展项数")
    result = model.extend(terms, count)
    print("扩展后：%s" % " ".join(str(item) for item in result))
    return 0


def _cmd_quiz(args: argparse.Namespace) -> int:
    count = _parse_int(args.count, "题目数量")
    seed = None if args.seed is None else _parse_int(args.seed, "随机种子")
    items = model.quiz_items(count, seed=seed, level=args.level)
    content = render.quiz_html(
        items,
        title="数列规律练习",
        with_answers=bool(args.answers),
        level=args.level,
    )
    return _emit(content, args.output)


def _cmd_poster(args: argparse.Namespace) -> int:
    return _emit(render.poster_html(), args.output)


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="numberpatterns",
        description="数列规律：识别递增规律、预测下一项、生成可打印练习页。",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="命令")

    next_parser = subparsers.add_parser("next", help="预测下一项")
    next_parser.add_argument("numbers", nargs="+", metavar="数", help="数列各项")
    next_parser.set_defaults(handler=_cmd_next)

    rule_parser = subparsers.add_parser("rule", help="识别规律并说明")
    rule_parser.add_argument("numbers", nargs="+", metavar="数", help="数列各项")
    rule_parser.set_defaults(handler=_cmd_rule)

    candidates_parser = subparsers.add_parser(
        "candidates", help="列出所有成立的规律"
    )
    candidates_parser.add_argument(
        "numbers", nargs="+", metavar="数", help="数列各项"
    )
    candidates_parser.set_defaults(handler=_cmd_candidates)

    extend_parser = subparsers.add_parser("extend", help="按规律向后扩展")
    extend_parser.add_argument("numbers", nargs="+", metavar="数", help="数列各项")
    extend_parser.add_argument(
        "--count",
        default="3",
        metavar="N",
        help="扩展项数（1~20，默认 3）",
    )
    extend_parser.set_defaults(handler=_cmd_extend)

    quiz_parser = subparsers.add_parser("quiz", help="生成练习题 HTML")
    quiz_parser.add_argument(
        "--count",
        default="10",
        metavar="N",
        help="题目数量（1~30，默认 10）",
    )
    quiz_parser.add_argument(
        "--seed",
        default=None,
        metavar="S",
        help="随机种子，便于复现",
    )
    quiz_parser.add_argument(
        "--level",
        default="normal",
        metavar="LEVEL",
        help="难度：easy、normal 或 hard",
    )
    quiz_parser.add_argument(
        "--answers",
        action="store_true",
        help="附加参考答案页",
    )
    quiz_parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="文件",
        help="输出文件路径；省略时打印到终端",
    )
    quiz_parser.set_defaults(handler=_cmd_quiz)

    poster_parser = subparsers.add_parser("poster", help="生成 7 类规律速查表")
    poster_parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="文件",
        help="输出文件路径；省略时打印到终端",
    )
    poster_parser.set_defaults(handler=_cmd_poster)

    return parser


def _run(args: argparse.Namespace) -> int:
    """执行解析后的子命令，返回退出码。"""
    handler = getattr(args, "handler", None)
    if handler is None:
        raise ValueError("缺少子命令，请使用 --help 查看用法")
    if not callable(handler):
        raise TypeError("内部错误：子命令处理器无效")
    result = handler(args)
    if not isinstance(result, int) or isinstance(result, bool):
        raise TypeError("内部错误：子命令返回值必须是整数")
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主入口。"""
    _ensure_utf8_console()
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command is None:
            parser.print_help()
            return 0
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
