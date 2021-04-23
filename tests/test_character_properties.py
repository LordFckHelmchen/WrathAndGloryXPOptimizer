import unittest

from wrath_and_glory_xp_optimizer.character_properties import Attribute, Attributes, IntBounds, Skill, Skills


class TestIntBounds(unittest.TestCase):
    def test_values_within_bounds_expect_contains_is_true(self):
        bounds = IntBounds(-1, 1)
        for val in bounds.as_range():
            self.assertTrue(val in bounds, f"Value within bounds was not identified: {val} in {bounds}!")

    def test_values_outside_bounds_expect_contains_is_false(self):
        bounds = IntBounds(-8, 12)
        for val in [bounds.min - 1, bounds.max + 1]:
            self.assertFalse(bounds.min - 1 in bounds, f"Out-of-bound value was not identified: {val} not in {bounds}!")

    def test_as_range_expect_bounds_to_be_met(self):
        min_val = -12
        max_val = 0
        bounds = IntBounds(min_val, max_val).as_range()
        self.assertEqual(min_val, min(bounds))
        self.assertEqual(max_val, max(bounds))

    def test_init_with_out_of_order_limits_expect_ordered_bounds(self):
        min_val = 7
        max_val = 100
        bounds = IntBounds(max_val, min_val)
        self.assertEqual(min_val, bounds.min)
        self.assertEqual(max_val, bounds.max)

    def test_add_int_expect_correct_results(self):
        min_val = -56
        max_val = -2
        add_val = 5
        expected_bounds = IntBounds(min_val + add_val, max_val + add_val)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)

    def test_add_IntBounds_expect_correct_results(self):
        min_val = -7
        max_val = 236
        add_val = IntBounds(-3, 5)
        expected_bounds = IntBounds(min_val + add_val.min, max_val + add_val.max)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)


class TestInvalidAttributeAndSkill(unittest.TestCase):
    def test_total_rating_bounds_expect_min_max_to_be_smaller_than_valid_min(self):
        for property_class, invalid_property in zip([Attribute, Skill],
                                                    [Attributes.INVALID.value, Skills.INVALID.value]):
            for val in invalid_property.rating_bounds:
                with self.subTest(i=f"{type(invalid_property).__name__}: {val}"):
                    self.assertFalse(property_class.is_valid_rating(val))
                    self.assertLess(val, property_class.rating_bounds.min)

    def test_is_valid_rating_expect_false(self):
        for property_class, invalid_property in zip([Attribute, Skill],
                                                    [Attributes.INVALID.value, Skills.INVALID.value]):
            for val in [invalid_property.rating_bounds.min, property_class.rating_bounds.max]:
                with self.subTest(i=f"{type(invalid_property).__name__}: {val}"):
                    self.assertFalse(invalid_property.is_valid_rating(val))


class TestInvalidSkill(unittest.TestCase):
    def test_total_rating_expect_same_invalid_value_as_rating(self):
        self.assertEqual(Skills.INVALID.value.rating_bounds, Skills.INVALID.value.total_rating_bounds)

    def test_is_valid_total_rating_expect_false(self):
        for val in [Skills.INVALID.value.rating_bounds.min, Skill.rating_bounds.max]:
            with self.subTest(i=val):
                self.assertFalse(Skills.INVALID.value.is_valid_total_rating(val))
