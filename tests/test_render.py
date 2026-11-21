"""render 模块的单元测试。"""

from __future__ import annotations

import unittest
from typing import Dict, List

from numberpatterns import model
from numberpatterns.render import LEVEL_LABELS, poster_html, quiz_html


def _sample_items(count: int = 3) -> List[Dict[str, object]]:
    return model.quiz_items(count, seed=4, level="normal")


def _single_item() -> Dict[str, object]:
    return {
        "terms": [1, 4, 2, 5, 3, 6],
        "answer": 4,
        "rule": "alternating",
        "detail": "交替数列：奇数位与偶数位各自等差，公差为 1。",
    }


class TestQuizHtml(unittest.TestCase):
    """quiz_html 的测试。"""

    def test_returns_html_document(self) -> None:
        html_text = quiz_html(_sample_items(), "数列练习")
        self.assertIsInstance(html_text, str)
        self.assertIn("<!DOCTYPE html>", html_text)
        self.assertIn('lang="zh-CN"', html_text)
        self.assertIn('<meta charset="utf-8">', html_text)

    def test_title_is_rendered(self) -> None:
        html_text = quiz_html(_sample_items(), "五年级数列练习")
        self.assertIn("<title>五年级数列练习</title>", html_text)
        self.assertIn("<h1>五年级数列练习</h1>", html_text)

    def test_question_count(self) -> None:
        html_text = quiz_html(_sample_items(5), "练习")
        self.assertEqual(html_text.count('class="question"'), 5)

    def test_terms_are_rendered(self) -> None:
        html_text = quiz_html([_single_item()], "练习")
        self.assertIn("1, 4, 2, 5, 3, 6", html_text)
        self.assertIn('class="blank"', html_text)

    def test_answers_hidden_by_default(self) -> None:
        html_text = quiz_html(_sample_items(), "练习")
        self.assertNotIn('class="answers"', html_text)
        self.assertNotIn("参考答案", html_text)

    def test_answers_included_when_requested(self) -> None:
        html_text = quiz_html([_single_item()], "练习", with_answers=True)
        self.assertIn('class="answers"', html_text)
        self.assertIn("参考答案", html_text)
        self.assertIn('class="ans-value">4<', html_text)
        self.assertIn("交替数列", html_text)

    def test_meta_contains_level_and_count(self) -> None:
        html_text = quiz_html(_sample_items(4), "练习", level="hard")
        self.assertIn(LEVEL_LABELS["hard"], html_text)
        self.assertIn("共 4 题", html_text)

    def test_level_easy_label(self) -> None:
        html_text = quiz_html(_sample_items(2), "练习", level="easy")
        self.assertIn("简单", html_text)

    def test_title_is_escaped(self) -> None:
        html_text = quiz_html([_single_item()], "<script>alert(1)</script>")
        self.assertNotIn("<script>alert(1)</script>", html_text)
        self.assertIn("&lt;script&gt;", html_text)

    def test_detail_is_escaped(self) -> None:
        item = _single_item()
        item["detail"] = '<img src="x" onerror="alert(1)">'
        html_text = quiz_html([item], "练习", with_answers=True)
        self.assertNotIn('<img src="x"', html_text)
        self.assertIn("&lt;img", html_text)

    def test_print_styles_present(self) -> None:
        html_text = quiz_html(_sample_items(), "练习")
        self.assertIn("@media print", html_text)
        self.assertIn("@page", html_text)
        self.assertIn("A4", html_text)
        self.assertIn("page-break-before: always", html_text)

    def test_empty_items_allowed(self) -> None:
        html_text = quiz_html([], "练习")
        self.assertIn("共 0 题", html_text)
        self.assertEqual(html_text.count('class="question"'), 0)

    def test_non_sequence_items_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html("not-a-list", "练习")  # type: ignore[arg-type]

    def test_item_not_dict_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html([1, 2], "练习")  # type: ignore[list-item]

    def test_missing_key_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html([{"terms": [1, 2, 3, 4]}], "练习")

    def test_empty_terms_raise_value_error(self) -> None:
        item = _single_item()
        item["terms"] = []
        with self.assertRaises(ValueError):
            quiz_html([item], "练习")

    def test_string_terms_raise_type_error(self) -> None:
        item = _single_item()
        item["terms"] = "1234"
        with self.assertRaises(TypeError):
            quiz_html([item], "练习")

    def test_float_terms_raise_type_error(self) -> None:
        item = _single_item()
        item["terms"] = [1.5, 2, 3, 4]
        with self.assertRaises(TypeError):
            quiz_html([item], "练习")

    def test_bool_answer_raises_type_error(self) -> None:
        item = _single_item()
        item["answer"] = True
        with self.assertRaises(TypeError):
            quiz_html([item], "练习")

    def test_non_str_title_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(_sample_items(), 123)  # type: ignore[arg-type]

    def test_non_bool_with_answers_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(_sample_items(), "练习", with_answers="yes")  # type: ignore[arg-type]

    def test_invalid_level_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html(_sample_items(), "练习", level="insane")

    def test_non_str_level_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(_sample_items(), "练习", level=1)  # type: ignore[arg-type]


class TestPosterHtml(unittest.TestCase):
    """poster_html 的测试。"""

    def test_returns_html_document(self) -> None:
        html_text = poster_html()
        self.assertIn("<!DOCTYPE html>", html_text)
        self.assertIn('lang="zh-CN"', html_text)
        self.assertIn("<title>数列规律速查表</title>", html_text)

    def test_contains_all_rule_labels(self) -> None:
        html_text = poster_html()
        for label in model.RULE_LABELS.values():
            self.assertIn(label, html_text)

    def test_contains_examples(self) -> None:
        html_text = poster_html()
        self.assertIn("1, 4, 9, 16", html_text)
        self.assertIn("1, 4, 2, 5, 3, 6", html_text)
        self.assertIn("2, 5, 10, 17", html_text)

    def test_table_has_seven_rule_rows(self) -> None:
        html_text = poster_html()
        self.assertEqual(html_text.count("<tr>"), 8)
        self.assertIn("<tbody>", html_text)

    def test_print_styles_present(self) -> None:
        html_text = poster_html()
        self.assertIn("@media print", html_text)
        self.assertIn("@page", html_text)
        self.assertIn("A4", html_text)

    def test_no_external_resources(self) -> None:
        html_text = poster_html()
        self.assertNotIn("http://", html_text)
        self.assertNotIn("https://", html_text)


if __name__ == "__main__":
    unittest.main()
