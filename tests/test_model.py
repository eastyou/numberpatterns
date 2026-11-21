"""model 模块的单元测试。"""

from __future__ import annotations

import unittest
from typing import Dict

from numberpatterns import model


class TestValidation(unittest.TestCase):
    """输入校验相关的测试。"""

    def test_empty_sequence_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([])

    def test_single_item_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([1])

    def test_two_items_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([1, 2])

    def test_three_items_without_fibonacci_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([1, 2, 4])

    def test_string_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect("1234")  # type: ignore[arg-type]

    def test_none_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect(None)  # type: ignore[arg-type]

    def test_generator_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect(iter([1, 2, 3, 4]))  # type: ignore[arg-type]

    def test_set_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect({1, 2, 3, 4})  # type: ignore[arg-type]

    def test_float_item_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect([1.0, 2, 3, 4])  # type: ignore[list-item]

    def test_bool_item_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect([True, 2, 3, 4])

    def test_str_item_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.detect([1, "2", 3, 4])  # type: ignore[list-item]

    def test_too_large_item_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([1_000_001, 2, 3, 4])

    def test_too_negative_item_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([-1_000_001, 2, 3, 4])

    def test_range_input_is_accepted(self) -> None:
        info = model.detect(range(1, 5))
        self.assertEqual(info["rule"], "arithmetic")
        self.assertEqual(info["next"], 5)

    def test_tuple_input_is_accepted(self) -> None:
        info = model.detect((2, 4, 6, 8))
        self.assertEqual(info["rule"], "arithmetic")


class TestDetectRules(unittest.TestCase):
    """7 类规律的识别测试。"""

    def test_constant(self) -> None:
        info = model.detect([5, 5, 5, 5])
        self.assertEqual(info["rule"], "constant")
        self.assertEqual(info["next"], 5)
        self.assertIn("常数", str(info["detail"]))

    def test_arithmetic(self) -> None:
        info = model.detect([2, 4, 6, 8])
        self.assertEqual(info["rule"], "arithmetic")
        self.assertEqual(info["next"], 10)
        self.assertIn("公差为 2", str(info["detail"]))

    def test_arithmetic_negative_diff(self) -> None:
        info = model.detect([0, -2, -4, -6])
        self.assertEqual(info["rule"], "arithmetic")
        self.assertEqual(info["next"], -8)

    def test_geometric(self) -> None:
        info = model.detect([1, 3, 9, 27])
        self.assertEqual(info["rule"], "geometric")
        self.assertEqual(info["next"], 81)
        self.assertIn("公比为 3", str(info["detail"]))

    def test_geometric_negative_ratio(self) -> None:
        info = model.detect([2, -4, 8, -16])
        self.assertEqual(info["rule"], "geometric")
        self.assertEqual(info["next"], 32)

    def test_ratio_one_is_not_geometric(self) -> None:
        info = model.detect([3, 3, 3, 3])
        self.assertEqual(info["rule"], "constant")

    def test_ratio_zero_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([1, 0, 0, 0])

    def test_squares(self) -> None:
        info = model.detect([1, 4, 9, 16])
        self.assertEqual(info["rule"], "squares")
        self.assertEqual(info["next"], 25)
        self.assertIn("平方", str(info["detail"]))

    def test_squares_with_offset(self) -> None:
        info = model.detect([4, 9, 16, 25])
        self.assertEqual(info["rule"], "squares")
        self.assertEqual(info["next"], 36)

    def test_squares_from_zero(self) -> None:
        info = model.detect([0, 1, 4, 9])
        self.assertEqual(info["rule"], "squares")
        self.assertEqual(info["next"], 16)

    def test_fibonacci(self) -> None:
        info = model.detect([1, 1, 2, 3, 5])
        self.assertEqual(info["rule"], "fibonacci")
        self.assertEqual(info["next"], 8)
        self.assertIn("前两项之和", str(info["detail"]))

    def test_fibonacci_three_terms(self) -> None:
        info = model.detect([1, 1, 2])
        self.assertEqual(info["rule"], "fibonacci")
        self.assertEqual(info["next"], 3)

    def test_fibonacci_other_start(self) -> None:
        info = model.detect([2, 3, 5, 8])
        self.assertEqual(info["rule"], "fibonacci")
        self.assertEqual(info["next"], 13)

    def test_alternating(self) -> None:
        info = model.detect([1, 4, 2, 5, 3, 6])
        self.assertEqual(info["rule"], "alternating")
        self.assertEqual(info["next"], 4)
        self.assertIn("奇数位", str(info["detail"]))

    def test_alternating_other_values(self) -> None:
        info = model.detect([10, 7, 12, 9, 14, 11])
        self.assertEqual(info["rule"], "alternating")
        self.assertEqual(info["next"], 16)

    def test_quadratic(self) -> None:
        info = model.detect([2, 5, 10, 17])
        self.assertEqual(info["rule"], "quadratic")
        self.assertEqual(info["next"], 26)
        self.assertIn("二阶差分", str(info["detail"]))

    def test_quadratic_mixed_values(self) -> None:
        info = model.detect([1, 0, 1, 4])
        self.assertEqual(info["rule"], "quadratic")
        self.assertEqual(info["next"], 9)

    def test_quadratic_longer(self) -> None:
        info = model.detect([3, 6, 12, 21, 33])
        self.assertEqual(info["rule"], "quadratic")
        self.assertEqual(info["next"], 48)

    def test_unknown_sequence_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            model.detect([1, 2, 3, 6])


class TestPriority(unittest.TestCase):
    """多规律同时成立时的优先级测试。"""

    def test_constant_beats_arithmetic(self) -> None:
        info = model.detect([7, 7, 7, 7])
        self.assertEqual(info["rule"], "constant")

    def test_squares_beats_quadratic(self) -> None:
        info = model.detect([1, 4, 9, 16])
        self.assertEqual(info["rule"], "squares")
        self.assertIn("同时满足", str(info["detail"]))
        self.assertIn("二阶差分数列", str(info["detail"]))

    def test_arithmetic_beats_alternating(self) -> None:
        info = model.detect([1, 4, 7, 10])
        self.assertEqual(info["rule"], "arithmetic")


class TestCandidates(unittest.TestCase):
    """candidates 的测试。"""

    def test_squares_and_quadratic_both_listed(self) -> None:
        results = model.candidates([1, 4, 9, 16])
        rules = [item["rule"] for item in results]
        self.assertEqual(rules[0], "squares")
        self.assertIn("quadratic", rules)

    def test_constant_and_arithmetic_both_listed(self) -> None:
        results = model.candidates([5, 5, 5, 5])
        rules = [item["rule"] for item in results]
        self.assertEqual(rules[0], "constant")
        self.assertIn("arithmetic", rules)

    def test_geometric_only(self) -> None:
        results = model.candidates([1, 2, 4, 8])
        self.assertEqual([item["rule"] for item in results], ["geometric"])

    def test_candidates_items_have_public_keys(self) -> None:
        for item in model.candidates([2, 5, 10, 17]):
            self.assertEqual(
                sorted(item.keys()), ["detail", "next", "rule"]
            )

    def test_candidates_three_term_fibonacci(self) -> None:
        results = model.candidates([1, 1, 2])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["rule"], "fibonacci")

    def test_candidates_invalid_sequence(self) -> None:
        with self.assertRaises(ValueError):
            model.candidates([1, 2, 3, 6])


class TestNextTerm(unittest.TestCase):
    """next_term 的测试。"""

    def test_next_term_arithmetic(self) -> None:
        self.assertEqual(model.next_term([2, 4, 6, 8]), 10)

    def test_next_term_fibonacci(self) -> None:
        self.assertEqual(model.next_term([1, 1, 2, 3, 5]), 8)

    def test_next_term_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.next_term([])

    def test_next_term_bool_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.next_term([True, 2, 3, 4])


class TestExtend(unittest.TestCase):
    """extend 的测试。"""

    def test_extend_arithmetic(self) -> None:
        result = model.extend([2, 4, 6, 8], 3)
        self.assertEqual(result, [2, 4, 6, 8, 10, 12, 14])

    def test_extend_constant(self) -> None:
        self.assertEqual(model.extend([4, 4, 4, 4], 2), [4, 4, 4, 4, 4, 4])

    def test_extend_geometric(self) -> None:
        self.assertEqual(
            model.extend([1, 3, 9, 27], 2), [1, 3, 9, 27, 81, 243]
        )

    def test_extend_squares(self) -> None:
        self.assertEqual(model.extend([1, 4, 9, 16], 1), [1, 4, 9, 16, 25])

    def test_extend_fibonacci(self) -> None:
        self.assertEqual(
            model.extend([1, 1, 2, 3, 5], 2), [1, 1, 2, 3, 5, 8, 13]
        )

    def test_extend_fibonacci_three_terms(self) -> None:
        self.assertEqual(model.extend([1, 1, 2], 1), [1, 1, 2, 3])

    def test_extend_alternating(self) -> None:
        self.assertEqual(
            model.extend([1, 4, 2, 5, 3, 6], 2),
            [1, 4, 2, 5, 3, 6, 4, 7],
        )

    def test_extend_quadratic(self) -> None:
        self.assertEqual(
            model.extend([2, 5, 10, 17], 2),
            [2, 5, 10, 17, 26, 37],
        )

    def test_extend_does_not_mutate_input(self) -> None:
        terms = [2, 4, 6, 8]
        model.extend(terms, 3)
        self.assertEqual(terms, [2, 4, 6, 8])

    def test_extend_zero_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.extend([2, 4, 6, 8], 0)

    def test_extend_too_many_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.extend([2, 4, 6, 8], 21)

    def test_extend_non_int_count_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.extend([2, 4, 6, 8], "3")  # type: ignore[arg-type]

    def test_extend_bool_count_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.extend([2, 4, 6, 8], True)

    def test_extend_long_constant(self) -> None:
        result = model.extend([1, 1, 1, 1], 20)
        self.assertEqual(len(result), 24)
        self.assertTrue(all(item == 1 for item in result))

    def test_extend_invalid_terms(self) -> None:
        with self.assertRaises(ValueError):
            model.extend([1, 2, 3, 6], 1)


class TestGenerate(unittest.TestCase):
    """generate 的测试。"""

    def test_generate_constant(self) -> None:
        self.assertEqual(model.generate("constant", 3, 6), [3] * 6)

    def test_generate_arithmetic_structure(self) -> None:
        values = model.generate("arithmetic", -2, 6, seed=3)
        self.assertEqual(len(values), 6)
        self.assertEqual(values[0], -2)
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        self.assertEqual(len(set(diffs)), 1)
        self.assertNotEqual(diffs[0], 0)
        self.assertEqual(model.detect(values)["rule"], "arithmetic")

    def test_generate_geometric_structure(self) -> None:
        values = model.generate("geometric", 2, 5, seed=1)
        self.assertEqual(values[0], 2)
        ratios = [values[i + 1] // values[i] for i in range(len(values) - 1)]
        self.assertEqual(len(set(ratios)), 1)
        self.assertNotIn(ratios[0], (0, 1))
        self.assertEqual(model.detect(values)["rule"], "geometric")

    def test_generate_squares(self) -> None:
        self.assertEqual(
            model.generate("squares", 2, 4), [4, 9, 16, 25]
        )

    def test_generate_fibonacci_structure(self) -> None:
        values = model.generate("fibonacci", 0, 6, seed=3)
        self.assertEqual(len(values), 6)
        for index in range(2, len(values)):
            self.assertEqual(
                values[index], values[index - 1] + values[index - 2]
            )
        self.assertEqual(model.detect(values)["rule"], "fibonacci")

    def test_generate_alternating_structure(self) -> None:
        values = model.generate("alternating", 1, 6, seed=2)
        diffs = {values[i + 2] - values[i] for i in range(len(values) - 2)}
        self.assertEqual(len(diffs), 1)
        self.assertEqual(model.detect(values)["rule"], "alternating")

    def test_generate_quadratic_structure(self) -> None:
        values = model.generate("quadratic", 1, 5, seed=4)
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        second = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
        self.assertEqual(len(set(second)), 1)
        self.assertNotEqual(second[0], 0)
        self.assertEqual(model.detect(values)["rule"], "quadratic")

    def test_generate_same_seed_is_deterministic(self) -> None:
        first = model.generate("arithmetic", 0, 5, seed=7)
        second = model.generate("arithmetic", 0, 5, seed=7)
        self.assertEqual(first, second)

    def test_generate_different_seeds_vary(self) -> None:
        variants = {
            tuple(model.generate("arithmetic", 0, 5, seed=value))
            for value in range(10)
        }
        self.assertGreater(len(variants), 1)

    def test_generate_unknown_rule_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("triangular", 1, 5)

    def test_generate_non_str_rule_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.generate(123, 1, 5)  # type: ignore[arg-type]

    def test_generate_count_too_small_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("constant", 1, 3)

    def test_generate_count_too_large_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("constant", 1, 13)

    def test_generate_non_int_count_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.generate("constant", 1, "5")  # type: ignore[arg-type]

    def test_generate_non_int_start_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.generate("constant", 1.5, 5)  # type: ignore[arg-type]

    def test_generate_bool_start_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.generate("constant", True, 5)

    def test_generate_start_out_of_range_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("constant", 1_000_001, 5)

    def test_generate_geometric_zero_start_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("geometric", 0, 5)

    def test_generate_squares_negative_start_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("squares", -1, 5)

    def test_generate_non_int_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.generate("constant", 1, 5, seed="7")  # type: ignore[arg-type]

    def test_generate_bool_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.generate("constant", 1, 5, seed=True)

    def test_generate_overflow_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.generate("fibonacci", 1_000_000, 12, seed=1)


class TestQuiz(unittest.TestCase):
    """quiz_items 的测试。"""

    def _assert_item_shape(self, item: Dict[str, object]) -> None:
        self.assertIn("terms", item)
        self.assertIn("answer", item)
        self.assertIn("rule", item)
        self.assertIn("detail", item)
        terms = item["terms"]
        self.assertIsInstance(terms, list)
        self.assertIn(len(terms), (4, 5))
        for term in terms:
            self.assertIsInstance(term, int)
            self.assertNotIsInstance(term, bool)
            self.assertLessEqual(abs(term), 1_000_000)
        self.assertIsInstance(item["answer"], int)
        self.assertIsInstance(item["rule"], str)
        self.assertIsInstance(item["detail"], str)

    def test_quiz_item_shape(self) -> None:
        for item in model.quiz_items(5, seed=5):
            self._assert_item_shape(item)

    def test_quiz_answers_are_consistent(self) -> None:
        for item in model.quiz_items(10, seed=11):
            info = model.detect(item["terms"])
            self.assertEqual(item["answer"], info["next"])
            self.assertEqual(item["rule"], info["rule"])

    def test_quiz_easy_rules(self) -> None:
        allowed = {"constant", "arithmetic", "geometric"}
        for item in model.quiz_items(20, seed=1, level="easy"):
            self.assertIn(item["rule"], allowed)

    def test_quiz_normal_rules(self) -> None:
        allowed = {
            "constant",
            "arithmetic",
            "geometric",
            "squares",
            "fibonacci",
        }
        for item in model.quiz_items(20, seed=2, level="normal"):
            self.assertIn(item["rule"], allowed)

    def test_quiz_hard_rules(self) -> None:
        allowed = set(model.RULE_ORDER)
        for item in model.quiz_items(20, seed=3, level="hard"):
            self.assertIn(item["rule"], allowed)

    def test_quiz_count_one(self) -> None:
        items = model.quiz_items(1, seed=0)
        self.assertEqual(len(items), 1)

    def test_quiz_max_count(self) -> None:
        items = model.quiz_items(30, seed=0)
        self.assertEqual(len(items), 30)

    def test_quiz_same_seed_is_deterministic(self) -> None:
        first = model.quiz_items(8, seed=9, level="hard")
        second = model.quiz_items(8, seed=9, level="hard")
        self.assertEqual(first, second)

    def test_quiz_without_seed_works(self) -> None:
        self.assertEqual(len(model.quiz_items(3)), 3)

    def test_quiz_zero_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.quiz_items(0)

    def test_quiz_too_many_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.quiz_items(31)

    def test_quiz_non_int_count_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.quiz_items("5")  # type: ignore[arg-type]

    def test_quiz_bool_count_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.quiz_items(True)

    def test_quiz_invalid_level_raises(self) -> None:
        with self.assertRaises(ValueError):
            model.quiz_items(5, level="insane")

    def test_quiz_non_str_level_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.quiz_items(5, level=1)  # type: ignore[arg-type]

    def test_quiz_non_int_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            model.quiz_items(5, seed="1")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
