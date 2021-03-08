import json
import unittest
from dataclasses import dataclass
from typing import Dict

from characterProperties import Tier, IntBounds, Attributes, Skills, Traits
from xpOptimizer import AttributeSkillOptimizer, CharacterPropertyResults, XPCost, is_valid_target_values_dict, \
    AttributeSkillOptimizerResults


@dataclass
class IntendedSelection:
    tier: int
    target_values: Dict[str, int]
    expected_xp_cost: XPCost


class TestPropertyResults(unittest.TestCase):
    def test_missed_getter_expect_name_of_missed_value_if_total_is_smaller_than_target(self):
        value_name = 'val2'
        target_value = 3
        total_value = target_value - 1
        result = CharacterPropertyResults(total_values={value_name: total_value},
                                          target_values={value_name: target_value})
        self.assertEqual([value_name], result.Missed)

    def test_missed_getter_expect_empty_if_total_is_equal_or_larger_than_target(self):
        value_name = 'val2'
        target_value = 3
        for total_value in [target_value, target_value + 1]:
            result = CharacterPropertyResults(total_values={value_name: total_value},
                                              target_values={value_name: target_value})
            self.assertFalse(any(result.Missed))


class TestXPCost(unittest.TestCase):
    def test_Total_setter_expect_IOError_if_sum_is_incorrect(self):
        attribute_costs = 1
        skill_costs = 2
        total_costs = attribute_costs + skill_costs
        self.assertEqual(total_costs, XPCost(attribute_costs, skill_costs, total_costs).Total)
        self.assertEqual(total_costs, XPCost(attribute_costs, skill_costs).Total)  # Should not throw
        with self.assertRaises(IOError):
            XPCost(attribute_costs, skill_costs, total_costs + 1)


class TestAttributeSkillOptimizer(unittest.TestCase):
    def run_positive_tests_on_optimized_selection(self, selection: IntendedSelection) -> AttributeSkillOptimizerResults:
        optimizer = AttributeSkillOptimizer(tier=selection.tier)
        result = optimizer.optimize_selection(target_values=selection.target_values)

        self.maxDiff = None
        for property_name in ['Attributes', 'Skills', 'Traits']:
            missed_targets = result.__getattribute__(property_name).Missed
            self.assertFalse(any(missed_targets),
                             msg=f"Missed values were not empty:\n{repr(missed_targets)}\nResult{str(result)}")
        self.assertEqual(selection.expected_xp_cost, result.XPCost, msg=f"\nResult{str(result)}")

        return result

    def test_optimize_selection_expect_no_missed_targets_and_expected_xp_cost(self):
        selections = [IntendedSelection(tier=2,
                                        target_values={"Intellect": 5,
                                                       "Investigation": 10,
                                                       "Medicae": 10,
                                                       "Scholar": 15,
                                                       "Tech": 10,
                                                       "MaxWounds": 7},
                                        expected_xp_cost=XPCost(attribute_costs=120, skill_costs=80)),
                      IntendedSelection(tier=1,
                                        target_values={"Athletics": 5,
                                                       "Awareness": 3,
                                                       "BallisticSkill": 7,
                                                       "Cunning": 2,
                                                       "Stealth": 10},
                                        expected_xp_cost=XPCost(attribute_costs=45, skill_costs=50)),
                      IntendedSelection(tier=2,
                                        target_values={"Strength": 5,
                                                       "Toughness": 5,
                                                       "Willpower": 2,
                                                       "BallisticSkill": 2,
                                                       "Survival": 4,
                                                       "WeaponSkill": 8},
                                        expected_xp_cost=XPCost(attribute_costs=84, skill_costs=42))]
        for selection_id, selection in enumerate(selections):
            with self.subTest(i=selection_id):
                self.run_positive_tests_on_optimized_selection(selection)

    def test_optimize_selection_with_no_target_values_expect_0_cost_attributes_at_1_and_skills_at_0(self):
        target_values = dict()
        initial_attribute_total = 1
        initial_skill_rating = 0
        expected_attribute_totals = {member.name: initial_attribute_total for member in Attributes.get_valid_members()}
        expected_skill_ratings = {member.name: initial_skill_rating for member in Skills.get_valid_members()}
        expected_skill_totals = {member.name: initial_attribute_total for member in Skills.get_valid_members()}
        expected_xp_costs = XPCost(attribute_costs=0, skill_costs=0)

        optimizer = AttributeSkillOptimizer(tier=1)
        result = optimizer.optimize_selection(target_values=target_values)

        self.maxDiff = None
        self.assertDictEqual(expected_attribute_totals, result.Attributes.Total)
        self.assertDictEqual(expected_skill_ratings, result.Skills.Rating)
        self.assertDictEqual(expected_skill_totals, result.Skills.Total)
        self.assertEqual(expected_xp_costs, result.XPCost)

    def test_markdown_table_formatting_expect_match_to_stored_table(self):
        # noinspection PyPep8Naming
        EXPECTED_RESULTS_FILE_NAME = "TestChar_ExpectedResults"
        selection = IntendedSelection(tier=3,
                                      target_values={"Agility": 5,
                                                     "BallisticSkill": 11,
                                                     "Cunning": 7,
                                                     "Deception": 8,
                                                     "Stealth": 13,
                                                     "Defence": 6,
                                                     "MaxWounds": 10},
                                      expected_xp_cost=XPCost(attribute_costs=190, skill_costs=116))
        result = self.run_positive_tests_on_optimized_selection(selection)

        for extension, formatter in zip(["md", "json"], [lambda x: str(x), lambda x: json.dumps(dict(x), indent=2)]):
            expected_results_file_name = f"{EXPECTED_RESULTS_FILE_NAME}.{extension}"
            with open(expected_results_file_name, "r") as expected_results_file:
                expected_results = expected_results_file.read()
                self.assertEqual(expected_results, formatter(result))

            # Use this to re-create the files on updates of the format.
            # with open(expected_results_file_name, "w") as expected_results_file:
            #     expected_results_file.write(formatter(result))


class TestIsValidTargetValuesDict(unittest.TestCase):
    @staticmethod
    def get_minimal_valid_target_values() -> Dict[str, int]:
        return {Tier.full_name: Tier.rating_bounds.min}

    def assert_is_invalid_target_values_dict(self, target_values: Dict):
        self.assertFalse(is_valid_target_values_dict(target_values),
                         f"Expected target values dict to be invalid: {target_values}")

    def run_invalid_values_test(self, valid_key: str, value_bounds: IntBounds):
        for invalid_value in ["1", 1.0, value_bounds.min - 1, value_bounds.max + 1]:
            with self.subTest(i=f"{valid_key}: {invalid_value}"):
                target_values = TestIsValidTargetValuesDict.get_minimal_valid_target_values()
                target_values[valid_key] = invalid_value
                self.assertFalse(is_valid_target_values_dict(target_values))

    def test_empty_dict_expect_False(self):
        self.assertFalse(is_valid_target_values_dict(dict()))

    def test_minimally_valid_target_values_expect_True(self):
        self.assertTrue(is_valid_target_values_dict(TestIsValidTargetValuesDict.get_minimal_valid_target_values()))

    def test_valid_keys_expect_True(self):
        target_values = TestIsValidTargetValuesDict.get_minimal_valid_target_values()
        valid_item = Attributes.Strength
        target_values[valid_item.name] = valid_item.value.rating_bounds.min
        valid_item = Skills.BallisticSkill
        target_values[valid_item.name] = valid_item.value.total_rating_bounds.min
        valid_item = Traits.MaxShock
        target_values[valid_item.name] = valid_item.value.get_rating_bounds(related_tier=1).min
        self.assertTrue(is_valid_target_values_dict(target_values))

    def test_invalid_keys_expect_False(self):
        # noinspection PyPep8Naming
        VALID_VALUE = 2
        for invalid_key in ["Str", "Ini", "Ballistic", "Shock", "Wealth", "Passive Awareness", "Test"]:
            with self.subTest(i=invalid_key):
                target_values = {**TestIsValidTargetValuesDict.get_minimal_valid_target_values(),
                                 invalid_key: VALID_VALUE}
                self.assertFalse(is_valid_target_values_dict(target_values), target_values)

    def test_tier_only_dict_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Tier.full_name, value_bounds=Tier.rating_bounds)

    def test_attribute_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Attributes.Strength.name,
                                     value_bounds=Attributes.Strength.value.rating_bounds)

    def test_skills_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Skills.BallisticSkill.name,
                                     value_bounds=Skills.BallisticSkill.value.total_rating_bounds)

    def test_traits_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Traits.MaxWounds.name,
                                     value_bounds=Traits.MaxWounds.value.get_rating_bounds(related_tier=1))


if __name__ == '__main__':
    unittest.main()
