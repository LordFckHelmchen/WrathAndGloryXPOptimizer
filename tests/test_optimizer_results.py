import unittest

from tests.example_file_access import get_example_data

from wrath_and_glory_xp_optimizer.character_properties import Attributes
from wrath_and_glory_xp_optimizer.character_properties import Skills
from wrath_and_glory_xp_optimizer.character_properties import Traits
from wrath_and_glory_xp_optimizer.optimizer_core import AttributeSkillOptimizer
from wrath_and_glory_xp_optimizer.optimizer_results import CharacterPropertyResults


class TestPropertyResults(unittest.TestCase):
    def test_missed_getter_expect_name_of_missed_value_if_total_is_smaller_than_target(
        self,
    ):
        value_name = "val2"
        target_value = 3
        total_value = target_value - 1
        result = CharacterPropertyResults(
            Total={value_name: total_value}, Target={value_name: target_value}
        )
        self.assertEqual([value_name], result.Missed)

    def test_missed_getter_expect_empty_if_total_is_equal_or_larger_than_target(self):
        value_name = "val2"
        target_value = 3
        for total_value in [target_value, target_value + 1]:
            result = CharacterPropertyResults(
                Total={value_name: total_value}, Target={value_name: target_value}
            )
            self.assertFalse(
                any(result.Missed), f"Unexpected missed values found: {result.Missed}"
            )

    def test_formatting_functions_expect_match_to_stored_format(self):
        example_data = get_example_data()
        result = AttributeSkillOptimizer(
            example_data["target_values"]
        ).optimize_selection()

        self.maxDiff = None  # Show diff for long comparisons.
        for extension, formatter in zip(
            ["md", "json"], [lambda x: x.as_markdown(), lambda x: x.as_json()]
        ):
            with self.subTest(i=extension):
                self.assertEqual(
                    example_data["expected_results"][extension].rstrip(), formatter(result).rstrip()
                )

    def test_as_markdown_with_totals_below_equal_and_above_targets_expect_missed_only_for_below_target_values(
        self,
    ):
        expected_string = (
            "| Name           |   Total |   Target | Missed   |\n"
            "|----------------|---------|----------|----------|\n"
            "| Fellowship     |       7 |        5 | NO       |\n"
            "| BallisticSkill |       4 |        4 | NO       |\n"
            "| MaxShock       |       9 |       10 | YES      |"
        )
        results = CharacterPropertyResults(
            Target={
                Attributes.Fellowship.name: 5,
                Skills.BallisticSkill.name: 4,
                Traits.MaxShock.name: 10,
            },
            Total={
                Attributes.Fellowship.name: 7,
                Skills.BallisticSkill.name: 4,
                Traits.MaxShock.name: 9,
            },
        )
        self.assertEqual(expected_string, results.as_markdown())
