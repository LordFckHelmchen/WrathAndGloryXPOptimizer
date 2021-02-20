import unittest
from dataclasses import dataclass
from enum import EnumMeta
from typing import Callable, List, Any, Dict

from xpOptimizer import Attribute, Skill, DerivedProperty, StringEnum, AttributeSkillOptimizer, PropertyResults, XPCost


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
        result = PropertyResults(total_values={value_name: total_value}, target_values={value_name: target_value})
        self.assertEqual([value_name], result.Missed)

    def test_missed_getter_expect_empty_if_total_is_equal_or_larger_than_target(self):
        value_name = 'val2'
        target_value = 3
        for total_value in [target_value, target_value + 1]:
            result = PropertyResults(total_values={value_name: total_value}, target_values={value_name: target_value})
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


class TestStringEnum(unittest.TestCase):
    def run_tests_on_string_enums(self, assertions: List[Callable[[EnumMeta, StringEnum], Any]]):
        for StringEnumClass, member in zip([Attribute, Skill, DerivedProperty],
                                           [Attribute.Agility, Skill.BallisticSkill, DerivedProperty.MaxShock]):
            with self.subTest(i=StringEnumClass):
                for assertion in assertions:
                    assertion(StringEnumClass, member)

    def test_from_value_with_member_names_expect_members(self):
        def assert_member_name_results_in_member(enum_class: EnumMeta, enum_member: StringEnum):
            self.assertEqual(enum_member, enum_class.from_name_or_value(enum_member.value))

        self.run_tests_on_string_enums([assert_member_name_results_in_member])
        self.assertEqual(Attribute.Strength, Attribute.from_name_or_value("Strength"))

    def test_from_value_with_non_members_expect_none(self):
        def assert_non_member_name_results_in_none(enum_class: EnumMeta, enum_member: StringEnum):
            self.assertIsNone(enum_class.from_name_or_value('not-' + enum_member.value))

        def assert_member_name_with_added_whitespace_results_in_none(enum_class: EnumMeta, enum_member: StringEnum):
            self.assertIsNone(enum_class.from_name_or_value(enum_member.value + ' '))

        self.run_tests_on_string_enums([assert_non_member_name_results_in_none,
                                        assert_member_name_with_added_whitespace_results_in_none])

    def test_is_value_with_member_expect_true(self):
        def assert_member_name_results_in_true(enum_class: EnumMeta, enum_member: StringEnum):
            self.assertTrue(enum_class.is_value(enum_member.value))

        self.run_tests_on_string_enums([assert_member_name_results_in_true])

    def test_is_value_with_non_member_expect_false(self):
        def assert_non_member_name_results_in_false(enum_class: EnumMeta, enum_member: StringEnum):
            self.assertFalse(enum_class.is_value('not-' + enum_member.value))

        def assert_member_name_with_added_whitespace_results_in_false(enum_class: EnumMeta, enum_member: StringEnum):
            self.assertFalse(enum_class.is_value(enum_member.value + ' '))

        self.run_tests_on_string_enums([assert_non_member_name_results_in_false,
                                        assert_member_name_with_added_whitespace_results_in_false])


class TestAttributeSkillOptimizer(unittest.TestCase):
    def run_positive_tests_on_optimize_selection(self, selection: IntendedSelection):
        optimizer = AttributeSkillOptimizer(tier=selection.tier)
        result = optimizer.optimize_selection(target_values=selection.target_values)

        self.maxDiff = None
        for property_name in ['Attributes', 'Skills', 'DerivedProperties']:
            missed_targets = result.__getattribute__(property_name).Missed
            self.assertFalse(any(missed_targets),
                             msg=f"Missed values were not empty:\n{repr(missed_targets)}\nResult{str(result)}")
        self.assertEqual(selection.expected_xp_cost, result.XPCost, msg=f"\nResult{str(result)}")

    def test_name_to_enum_with_members_expect_string_enum(self):
        for name in ['I', 'PsychicMastery', 'Conviction']:
            self.assertIsInstance(AttributeSkillOptimizer.name_to_enum(name), StringEnum)

    def test_name_to_enum_with_non_members_expect_key_error(self):
        for name in ['Stupidity', 'MaWo', '1']:
            with self.assertRaises(KeyError):
                AttributeSkillOptimizer.name_to_enum(name)

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
                self.run_positive_tests_on_optimize_selection(selection)

    def test_optimize_selection_with_no_target_values_expect_0_cost_attributes_at_1_and_skills_at_0(self):
        target_values = dict()
        initial_attribute_total = 1
        initial_skill_rating = 0
        expected_attribute_totals = {name.name: initial_attribute_total for name in Attribute}
        expected_skill_ratings = {name.name: initial_skill_rating for name in Skill}
        expected_skill_totals = {name.name: initial_attribute_total for name in Skill}
        expected_xp_costs = XPCost(attribute_costs=0, skill_costs=0)

        optimizer = AttributeSkillOptimizer(tier=1)
        result = optimizer.optimize_selection(target_values=target_values)

        self.maxDiff = None
        self.assertDictEqual(expected_attribute_totals, result.Attributes.Total)
        self.assertDictEqual(expected_skill_ratings, result.Skills.Rating)
        self.assertDictEqual(expected_skill_totals, result.Skills.Total)
        self.assertEqual(expected_xp_costs, result.XPCost)


if __name__ == '__main__':
    unittest.main()
