import unittest
from dataclasses import dataclass
from typing import Dict

from wrath_and_glory_xp_optimizer.character_properties import Tier, IntBounds, Attributes, Skills, Traits
from wrath_and_glory_xp_optimizer.optimizer_core import AttributeSkillOptimizer, is_valid_target_values_dict
from wrath_and_glory_xp_optimizer.optimizer_results import XPCost, AttributeSkillOptimizerResults
from wrath_and_glory_xp_optimizer.exceptions import InvalidTargetValueException


@dataclass
class IntendedSelection:
    tier: int
    target_values: Dict[str, int]
    expected_xp_cost: XPCost


class TestAttributeSkillOptimizer(unittest.TestCase):
    def run_positive_tests_on_optimized_selection(self, selection: IntendedSelection) -> AttributeSkillOptimizerResults:
        optimizer = AttributeSkillOptimizer(tier=selection.tier)
        result = optimizer.optimize_selection(target_values=selection.target_values)

        self.maxDiff = None  # Show diff for long comparisons.
        for property_name in ['Attributes', 'Skills', 'Traits']:
            missed_targets = result.__getattribute__(property_name).Missed
            self.assertFalse(any(missed_targets),
                             f"Missed values were not empty:\n{repr(missed_targets)}\nResult{str(result)}")
        self.assertEqual(selection.expected_xp_cost, result.XPCost, f"\nResult{str(result)}")

        return result

    def test_optimize_selection_expect_no_missed_targets_and_expected_xp_cost(self):
        selections = [IntendedSelection(tier=2,
                                        target_values={"Intellect": 5,
                                                       "Investigation": 10,
                                                       "Medicae": 10,
                                                       "Scholar": 15,
                                                       "Tech": 10,
                                                       "MaxWounds": 7},
                                        expected_xp_cost=XPCost(Attributes=120, Skills=80)),
                      IntendedSelection(tier=1,
                                        target_values={"Athletics": 5,
                                                       "Awareness": 3,
                                                       "BallisticSkill": 7,
                                                       "Cunning": 2,
                                                       "Stealth": 10},
                                        expected_xp_cost=XPCost(Attributes=45, Skills=50)),
                      IntendedSelection(tier=2,
                                        target_values={"Strength": 5,
                                                       "Toughness": 5,
                                                       "Willpower": 2,
                                                       "BallisticSkill": 2,
                                                       "Survival": 4,
                                                       "WeaponSkill": 8},
                                        expected_xp_cost=XPCost(Attributes=84, Skills=42))]
        for selection_id, selection in enumerate(selections):
            with self.subTest(i=selection_id):
                self.run_positive_tests_on_optimized_selection(selection)

    def test_optimize_selection_with_no_target_values_expect_tier_1_cost_0_attributes_at_1_and_skills_at_0(self):
        target_values = dict()
        initial_attribute_total = 1
        initial_skill_rating = 0
        expected_attribute_totals = {member.name: initial_attribute_total for member in Attributes.get_valid_members()}
        expected_skill_ratings = {member.name: initial_skill_rating for member in Skills.get_valid_members()}
        expected_skill_totals = {member.name: initial_attribute_total for member in Skills.get_valid_members()}
        expected_xp_costs = XPCost(Attributes=0, Skills=0)

        optimizer = AttributeSkillOptimizer()
        result = optimizer.optimize_selection(target_values=target_values)

        self.maxDiff = None
        self.assertEqual(1, optimizer.tier)
        self.assertDictEqual(expected_attribute_totals, result.Attributes.Total)
        self.assertDictEqual(expected_skill_ratings, result.Skills.Rating)
        self.assertDictEqual(expected_skill_totals, result.Skills.Total)
        self.assertEqual(expected_xp_costs, result.XPCost)

    def test_optimize_selection_with_invalid_target_values_expect_InvalidTargetValuesException(self):
        invalid_target_values = {"Tier": 1,
                                 "Strength": 3,
                                 "Perception": 1,
                                 "Endurance": 1,
                                 "Charisma": 1,
                                 "Intelligence": 9,
                                 "Agility": 8,
                                 "Luck": 1}
        optimizer = AttributeSkillOptimizer(tier=invalid_target_values["Tier"])
        with self.assertRaises(InvalidTargetValueException):
            optimizer.optimize_selection(invalid_target_values)

    def test_init_with_out_of_bounds_tier_expect_clipping_to_closest_bound(self):
        for expected_tier, bound_offset in zip(list(Tier.rating_bounds), [-1, 1]):
            with self.subTest(i=f"Tier: {expected_tier + bound_offset}"):
                optimizer = AttributeSkillOptimizer(tier=expected_tier + bound_offset)
                self.assertEqual(expected_tier, optimizer.tier)


class TestIsValidTargetValuesDict(unittest.TestCase):
    @staticmethod
    def get_minimal_valid_target_values() -> Dict[str, int]:
        return {Tier.full_name: Tier.rating_bounds.min}

    def assert_is_valid_target_values_dict(self, target_values: Dict):
        self.assertTrue(is_valid_target_values_dict(target_values),
                        f"Valid target values dict was not detected: {target_values}")

    def assert_is_invalid_target_values_dict(self, target_values: Dict):
        self.assertFalse(is_valid_target_values_dict(target_values),
                         f"Expected target values dict to be invalid: {target_values}")

    def run_invalid_values_test(self, valid_key: str, value_bounds: IntBounds):
        for invalid_value in ["1", 1.0, value_bounds.min - 1, value_bounds.max + 1]:
            with self.subTest(i=f"{valid_key}: {invalid_value}"):
                target_values = TestIsValidTargetValuesDict.get_minimal_valid_target_values()
                target_values[valid_key] = invalid_value
                self.assert_is_invalid_target_values_dict(target_values)

    def test_empty_dict_expect_False(self):
        self.assert_is_invalid_target_values_dict(dict())

    def test_minimally_valid_target_values_expect_True(self):
        self.assert_is_valid_target_values_dict(TestIsValidTargetValuesDict.get_minimal_valid_target_values())

    def test_valid_keys_expect_True(self):
        target_values = TestIsValidTargetValuesDict.get_minimal_valid_target_values()
        valid_item = Attributes.Strength
        target_values[valid_item.name] = valid_item.value.rating_bounds.min
        valid_item = Skills.BallisticSkill
        target_values[valid_item.name] = valid_item.value.total_rating_bounds.min
        valid_item = Traits.MaxShock
        target_values[valid_item.name] = valid_item.value.get_rating_bounds(related_tier=1).min
        self.assert_is_valid_target_values_dict(target_values)

    def test_invalid_keys_expect_False(self):
        # noinspection PyPep8Naming
        VALID_VALUE = 2
        for invalid_key in ["Str", "Ini", "Ballistic", "Shock", "Wealth", "Passive Awareness", "Test"]:
            with self.subTest(i=invalid_key):
                target_values = {**TestIsValidTargetValuesDict.get_minimal_valid_target_values(),
                                 invalid_key: VALID_VALUE}
                self.assert_is_invalid_target_values_dict(target_values)

    def test_tier_only_dict_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Tier.full_name, value_bounds=Tier.rating_bounds)

    def test_non_string_key_dict_expect_False(self):
        target_values = TestIsValidTargetValuesDict.get_minimal_valid_target_values()
        # Also test a non-string key.
        # noinspection PyTypeChecker
        target_values[5] = 1
        self.assert_is_invalid_target_values_dict(target_values)

    def test_attribute_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Attributes.Strength.name,
                                     value_bounds=Attributes.Strength.value.rating_bounds)

    def test_skills_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Skills.BallisticSkill.name,
                                     value_bounds=Skills.BallisticSkill.value.total_rating_bounds)

    def test_traits_expect_False_for_non_integer_or_out_of_bounds_values(self):
        self.run_invalid_values_test(valid_key=Traits.MaxWounds.name,
                                     value_bounds=Traits.MaxWounds.value.get_rating_bounds(related_tier=1))
