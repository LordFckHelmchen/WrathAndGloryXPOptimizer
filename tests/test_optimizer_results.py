import unittest

from wrath_and_glory_xp_optimizer.optimizer_core import AttributeSkillOptimizer
from wrath_and_glory_xp_optimizer.optimizer_results import CharacterPropertyResults

from tests.example_file_access import get_example_data


class TestPropertyResults(unittest.TestCase):
    def test_missed_getter_expect_name_of_missed_value_if_total_is_smaller_than_target(self):
        value_name = 'val2'
        target_value = 3
        total_value = target_value - 1
        result = CharacterPropertyResults(Total={value_name: total_value},
                                          Target={value_name: target_value})
        self.assertEqual([value_name], result.Missed)

    def test_missed_getter_expect_empty_if_total_is_equal_or_larger_than_target(self):
        value_name = 'val2'
        target_value = 3
        for total_value in [target_value, target_value + 1]:
            result = CharacterPropertyResults(Total={value_name: total_value},
                                              Target={value_name: target_value})
            self.assertFalse(any(result.Missed), f"Unexpected missed values found: {result.Missed}")

    def test_formatting_functions_expect_match_to_stored_table(self):
        example_data = get_example_data()

        target_values = example_data["target_values"]
        optimizer = AttributeSkillOptimizer(tier=target_values.pop("Tier"))
        result = optimizer.optimize_selection(target_values=target_values)

        self.maxDiff = None  # Show diff for long comparisons.
        for extension, formatter in zip(["md", "json"], [lambda x: x.as_markdown(), lambda x: x.as_json()]):
            with self.subTest(i=extension):
                self.assertEqual(example_data["expected_results"][extension], formatter(result))
