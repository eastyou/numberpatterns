"""cli 模块的单元测试。"""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from typing import List, Tuple

from numberpatterns import cli


def _run(args: List[str]) -> Tuple[int, str, str]:
    """执行 CLI 并捕获标准输出与标准错误。"""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = cli.main(args)
    return code, stdout.getvalue(), stderr.getvalue()


class TestNextCommand(unittest.TestCase):
    """next 子命令测试。"""

    def test_next_arithmetic(self) -> None:
        code, out, err = _run(["next", "2", "4", "6", "8"])
        self.assertEqual(code, 0)
        self.assertIn("下一项：10", out)
        self.assertEqual(err, "")

    def test_next_negative_numbers(self) -> None:
        code, out, _err = _run(["next", "-2", "-4", "-6", "-8"])
        self.assertEqual(code, 0)
        self.assertIn("下一项：-10", out)

    def test_next_fibonacci(self) -> None:
        code, out, _err = _run(["next", "1", "1", "2", "3", "5"])
        self.assertEqual(code, 0)
        self.assertIn("下一项：8", out)


class TestRuleCommand(unittest.TestCase):
    """rule 子命令测试。"""

    def test_rule_squares(self) -> None:
        code, out, _err = _run(["rule", "1", "4", "9", "16"])
        self.assertEqual(code, 0)
        self.assertIn("规律：平方数列", out)
        self.assertIn("下一项：25", out)

    def test_rule_includes_detail(self) -> None:
        code, out, _err = _run(["rule", "2", "4", "6", "8"])
        self.assertEqual(code, 0)
        self.assertIn("说明：", out)
        self.assertIn("公差为 2", out)


class TestCandidatesCommand(unittest.TestCase):
    """candidates 子命令测试。"""

    def test_candidates_lists_multiple_rules(self) -> None:
        code, out, _err = _run(["candidates", "1", "4", "9", "16"])
        self.assertEqual(code, 0)
        self.assertIn("共有 2 种成立的规律", out)
        self.assertIn("平方数列", out)
        self.assertIn("二阶差分数列", out)


class TestExtendCommand(unittest.TestCase):
    """extend 子命令测试。"""

    def test_extend_with_count(self) -> None:
        code, out, _err = _run(["extend", "2", "4", "6", "8", "--count", "2"])
        self.assertEqual(code, 0)
        self.assertIn("扩展后：2 4 6 8 10 12", out)

    def test_extend_default_count(self) -> None:
        code, out, _err = _run(["extend", "2", "4", "6", "8"])
        self.assertEqual(code, 0)
        self.assertIn("扩展后：2 4 6 8 10 12 14", out)

    def test_extend_geometric(self) -> None:
        code, out, _err = _run(
            ["extend", "1", "3", "9", "27", "--count", "2"]
        )
        self.assertEqual(code, 0)
        self.assertIn("81 243", out)


class TestQuizCommand(unittest.TestCase):
    """quiz 子命令测试。"""

    def test_quiz_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "quiz.html")
            code, out, err = _run(
                [
                    "quiz",
                    "--count",
                    "3",
                    "--seed",
                    "1",
                    "--level",
                    "easy",
                    "-o",
                    target,
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn("已生成：%s" % target, out)
            self.assertTrue(os.path.exists(target))
            with open(target, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("共 3 题", content)

    def test_quiz_to_stdout(self) -> None:
        code, out, _err = _run(["quiz", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("共 2 题", out)

    def test_quiz_with_answers(self) -> None:
        code, out, _err = _run(
            ["quiz", "--count", "2", "--seed", "1", "--answers"]
        )
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_quiz_invalid_level(self) -> None:
        code, _out, err = _run(["quiz", "--level", "insane"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_quiz_zero_count(self) -> None:
        code, _out, err = _run(["quiz", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_quiz_non_numeric_count(self) -> None:
        code, _out, err = _run(["quiz", "--count", "abc"])
        self.assertEqual(code, 2)
        self.assertIn("题目数量必须是整数", err)

    def test_quiz_non_numeric_seed(self) -> None:
        code, _out, err = _run(["quiz", "--seed", "abc"])
        self.assertEqual(code, 2)
        self.assertIn("随机种子必须是整数", err)


class TestPosterCommand(unittest.TestCase):
    """poster 子命令测试。"""

    def test_poster_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "poster.html")
            code, out, _err = _run(["poster", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % target, out)
            with open(target, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("数列规律速查表", content)

    def test_poster_to_stdout(self) -> None:
        code, out, _err = _run(["poster"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("速查表", out)


class TestErrorHandling(unittest.TestCase):
    """错误处理与退出码测试。"""

    def test_invalid_number(self) -> None:
        code, _out, err = _run(["next", "1", "x", "3", "4"])
        self.assertEqual(code, 2)
        self.assertIn("数值格式错误", err)

    def test_too_few_terms(self) -> None:
        code, _out, err = _run(["next", "1", "2", "4"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_too_many_terms_for_extend_count(self) -> None:
        code, _out, err = _run(
            ["extend", "2", "4", "6", "8", "--count", "21"]
        )
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_unwritable_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "missing", "poster.html")
            code, _out, err = _run(["poster", "-o", target])
            self.assertEqual(code, 2)
            self.assertIn("无法写入文件", err)

    def test_no_arguments_prints_help(self) -> None:
        code, out, _err = _run([])
        self.assertEqual(code, 0)
        self.assertIn("usage", out)

    def test_help_option(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as context:
                cli.main(["--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("usage", stdout.getvalue())

    def test_unknown_command_exits(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as context:
                cli.main(["bogus"])
        self.assertEqual(context.exception.code, 2)

    def test_main_returns_int(self) -> None:
        code, _out, _err = _run(["next", "2", "4", "6", "8"])
        self.assertIsInstance(code, int)
        self.assertNotIsInstance(code, bool)


if __name__ == "__main__":
    unittest.main()
