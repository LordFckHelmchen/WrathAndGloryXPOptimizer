import unittest
from dataclasses import dataclass
from typing import Dict

from wrath_and_glory_xp_optimizer.character_properties.attributes import Attributes
from wrath_and_glory_xp_optimizer.character_properties.int_bounds import IntBounds
from wrath_and_glory_xp_optimizer.character_properties.skills import Skills
from wrath_and_glory_xp_optimizer.character_properties.tier import Tier
from wrath_and_glory_xp_optimizer.character_properties.traits import Traits
from wrath_and_glory_xp_optimizer.exceptions import InvalidTargetValueException
from wrath_and_glory_xp_optimizer.optimizer_core import AttributeSkillOptimizer
from wrath_and_glory_xp_optimizer.optimizer_core import managed_gekko_solver
from wrath_and_glory_xp_optimizer.optimizer_results import (
    AttributeSkillOptimizerResults,
)
from wrath_and_glory_xp_optimizer.optimizer_results import XPCost


@dataclass
class IntendedSelection:
    target_values: Dict[str, int]
    expected_xp_cost: XPCost


class TestAttributeSkillOptimizer(unittest.TestCase):
    @staticmethod
    def get_minimal_valid_target_values() -> Dict[str, int]:
        return {Tier.full_name: Tier.rating_bounds.min}

    def run_positive_tests_on_optimized_selection(
        self, selection: IntendedSelection
    ) -> AttributeSkillOptimizerResults:
        result = AttributeSkillOptimizer(selection.target_values).optimize_selection()

        self.maxDiff = None  # Show diff for long comparisons.
        for property_name in ["Attributes", "Skills", "Traits"]:
            missed_targets = result.__getattribute__(property_name).Missed
            self.assertFalse(
                any(missed_targets),
                f"Missed values were not empty:\n{repr(missed_targets)}\nResult{str(result)}",
            )
        self.assertEqual(
            selection.expected_xp_cost, result.XPCost, f"\nResult{str(result)}"
        )

        return result

    def assert_is_valid_target_values_dict(self, target_values: Dict):
        self.assertTrue(
            AttributeSkillOptimizer.is_valid_target_values_dict(target_values),
            f"Valid target values dict was not detected: {target_values}",
        )

    def assert_is_invalid_target_values_dict(self, target_values: Dict):
        self.assertFalse(
            AttributeSkillOptimizer.is_valid_target_values_dict(target_values),
            f"Expected target values dict to be invalid: {target_values}",
        )

    def run_invalid_values_test(self, valid_key: str, value_bounds: IntBounds):
        for invalid_value in ["1", 1.0, value_bounds.min - 1, value_bounds.max + 1]:
            with self.subTest(i=f"{valid_key}: {invalid_value}"):
                target_values = self.get_minimal_valid_target_values()
                target_values[valid_key] = invalid_value
                self.assert_is_invalid_target_values_dict(target_values)

    def test_optimize_selection_expect_no_missed_targets_and_expected_xp_cost(self):
        selections = [
            IntendedSelection(
                target_values={
                    Tier.full_name: 2,
                    Attributes.Intellect.name: 5,
                    Skills.Investigation.name: 10,
                    Skills.Medicae.name: 10,
                    Skills.Scholar.name: 15,
                    Skills.Tech.name: 10,
                    Traits.MaxWounds.name: 7,
                },
                expected_xp_cost=XPCost(Attributes=120, Skills=80),
            ),
            IntendedSelection(
                target_values={
                    Tier.full_name: 1,
                    Skills.Athletics.name: 5,
                    Skills.Awareness.name: 3,
                    Skills.BallisticSkill.name: 7,
                    Skills.Cunning.name: 2,
                    Skills.Stealth.name: 10,
                },
                expected_xp_cost=XPCost(Attributes=45, Skills=50),
            ),
            IntendedSelection(
                target_values={
                    Tier.full_name: 2,
                    Attributes.Strength.name: 5,
                    Attributes.Toughness.name: 5,
                    Attributes.Willpower.name: 2,
                    Skills.BallisticSkill.name: 2,
                    Skills.Survival.name: 4,
                    Skills.WeaponSkill.name: 8,
                },
                expected_xp_cost=XPCost(Attributes=84, Skills=42),
            ),
        ]
        for selection_id, selection in enumerate(selections):
            with self.subTest(i=selection_id):
                self.run_positive_tests_on_optimized_selection(selection)

    def test_optimize_selection_with_no_target_values_expect_tier_1_cost_0_attributes_at_1_and_skills_at_0(
        self,
    ):
        target_values = dict()
        initial_attribute_total = 1
        initial_skill_rating = 0
        expected_attribute_totals = {
            member.name: initial_attribute_total
            for member in Attributes.get_valid_members()
        }
        expected_skill_ratings = {
            member.name: initial_skill_rating for member in Skills.get_valid_members()
        }
        expected_skill_totals = {
            member.name: initial_attribute_total
            for member in Skills.get_valid_members()
        }
        expected_xp_costs = XPCost(Attributes=0, Skills=0)

        optimizer = AttributeSkillOptimizer(target_values)
        result = optimizer.optimize_selection()

        self.maxDiff = None
        self.assertEqual(1, optimizer.tier)
        self.assertDictEqual(expected_attribute_totals, result.Attributes.Total)
        self.assertDictEqual(expected_skill_ratings, result.Skills.Rating)
        self.assertDictEqual(expected_skill_totals, result.Skills.Total)
        self.assertEqual(expected_xp_costs, result.XPCost)

    def test_init_with_unknown_target_values_expect_InvalidTargetValuesException(self):
        invalid_target_values = {
            **self.get_minimal_valid_target_values(),
            Attributes.Strength.name: Attributes.Strength.value.rating_bounds.min,
            "Perception": 7,
            "Endurance": 2,
            "Charisma": 3,
            "Intelligence": 4,
            Attributes.Agility.name: Attributes.Agility.value.rating_bounds.max,
            "Luck": 8,
        }
        with self.assertRaises(InvalidTargetValueException):
            AttributeSkillOptimizer(invalid_target_values)

    def test_init_with_missing_tier_expect_tier_set_to_minimum(self):
        optimizer = AttributeSkillOptimizer(
            {
                Attributes.Fellowship.name: Attributes.Fellowship.value.rating_bounds.min,
                Skills.BallisticSkill.name: Skills.BallisticSkill.value.total_rating_bounds.max,
            }
        )
        self.assertEqual(Tier.rating_bounds.min, optimizer.tier)

    def test__get_gekko_var_expect_StopIteration_for_missing_property(self):
        with managed_gekko_solver(remote=False) as solver:
            # Define variables with optimized initial values.
            gekko_variables = [
                solver.Var(name="test_var_1"),
                solver.Var(name="test_var_2"),
            ]
            with self.assertRaises(StopIteration):
                AttributeSkillOptimizer._get_gekko_var(
                    Attributes.Fellowship, gekko_variables
                )

    def test_empty_dict_expect_False(self):
        self.assert_is_invalid_target_values_dict(dict())

    def test_is_valid_target_values_dict_with_minimally_valid_target_values_expect_True(
        self,
    ):
        self.assert_is_valid_target_values_dict(self.get_minimal_valid_target_values())

    def test_is_valid_target_values_dict_with_valid_keys_expect_true(self):
        target_values = self.get_minimal_valid_target_values()
        valid_item = Attributes.Strength
        target_values[valid_item.name] = valid_item.value.rating_bounds.min
        valid_item = Skills.BallisticSkill
        target_values[valid_item.name] = valid_item.value.total_rating_bounds.min
        valid_item = Traits.MaxShock
        target_values[valid_item.name] = valid_item.value.get_rating_bounds(
            related_tier=1
        ).min
        self.assert_is_valid_target_values_dict(target_values)

    def test_is_valid_target_values_dict_with_invalid_keys_expect_false(self):
        valid_value = 2
        for invalid_key in [
            "Str",
            "Ini",
            "Ballistic",
            "Shock",
            "Wealth",
            "Passive Awareness",
            "Test",
            5,
        ]:
            with self.subTest(i=invalid_key):
                target_values = {
                    **self.get_minimal_valid_target_values(),
                    invalid_key: valid_value,
                }
                self.assert_is_invalid_target_values_dict(target_values)

    def test_is_valid_target_values_dict_with_tier_only_dict_expect_false_for_non_integer_or_out_of_bounds_values(
        self,
    ):
        self.run_invalid_values_test(
            valid_key=Tier.full_name, value_bounds=Tier.rating_bounds
        )

    def test_is_valid_target_values_dict_with_attributes_expect_false_for_non_integer_or_out_of_bounds_values(
        self,
    ):
        self.run_invalid_values_test(
            valid_key=Attributes.Strength.name,
            value_bounds=Attributes.Strength.value.rating_bounds,
        )

    def test_is_valid_target_values_dict_with_skills_expect_false_for_non_integer_or_out_of_bounds_values(
        self,
    ):
        self.run_invalid_values_test(
            valid_key=Skills.BallisticSkill.name,
            value_bounds=Skills.BallisticSkill.value.total_rating_bounds,
        )

    def test_is_valid_target_values_dict_with_traits_expect_False_for_non_integer_or_out_of_bounds_values(
        self,
    ):
        self.run_invalid_values_test(
            valid_key=Traits.MaxWounds.name,
            value_bounds=Traits.MaxWounds.value.get_rating_bounds(related_tier=1),
        )
