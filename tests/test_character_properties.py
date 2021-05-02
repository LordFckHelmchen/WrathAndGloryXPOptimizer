import unittest

from wrath_and_glory_xp_optimizer.character_properties import Attribute, Attributes, IntBounds, Skill, Skills, Trait, Traits


class TestIntBounds(unittest.TestCase):
    def test_contains_with_values_within_bounds_expect_true(self):
        bounds = IntBounds(-1, 1)
        for val in bounds.as_range():
            with self.subTest(i=val):
                self.assertTrue(val in bounds, f"Value within bounds was not identified: {val} in {bounds}!")

    def test_contains_with_none_and_values_outside_bounds_expect_false(self):
        bounds = IntBounds(-8, 12)
        for val in [None, bounds.min - 1, bounds.max + 1]:
            with self.subTest(i=val):
                self.assertFalse(val in bounds, f"Out-of-bound value was not identified: {val} not in {bounds}!")

    def test_as_range_expect_bounds_to_be_met(self):
        min_val = -12
        max_val = 0
        bounds_as_range = IntBounds(min_val, max_val).as_range()
        self.assertEqual(min_val, min(bounds_as_range))
        self.assertEqual(max_val, max(bounds_as_range))

    def test_init_with_out_of_order_limits_expect_ordered_bounds(self):
        min_val = 7
        max_val = 100
        bounds = IntBounds(max_val, min_val)
        self.assertEqual(min_val, bounds.min)
        self.assertEqual(max_val, bounds.max)

    def test_init_with_none_in_bounds_expect_contains_to_be_always_false(self):
        min_val = None
        max_val = 666
        bounds = IntBounds(min_val, max_val)
        for val in [-1, min_val, max_val, max_val + 1]:
            with self.subTest(i=val):
                self.assertFalse(val in bounds)

    def test_init_with_none_in_bounds_expect_add_be_added_to_non_none_bound(self):
        min_val = 21
        max_val = None
        add_val = 21
        expected_bounds = IntBounds(min_val + add_val, None)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)

    def test_add_int_expect_correctly_added_bounds(self):
        min_val = -56
        max_val = -2
        add_val = 5
        expected_bounds = IntBounds(min_val + add_val, max_val + add_val)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)

    def test_add_none_expect_all_none_bounds(self):
        min_val = 752
        max_val = 98998
        add_val = None
        expected_bounds = IntBounds(None, None)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)

    def test_add_float_expect_TypeError(self):
        with self.assertRaises(TypeError):
            IntBounds(-1, 1) + 0.5

    def test_add_IntBounds_expect_correctly_added_bounds(self):
        min_val = -7
        max_val = 236
        add_val = IntBounds(-3, 5)
        expected_bounds = IntBounds(min_val + add_val.min, max_val + add_val.max)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)

    def test_iter_expect_values_in_correct_order(self):
        bounds = IntBounds(-22, 9)
        self.assertEqual([bounds.min, bounds.max], [*bounds])

    def test_are_valid_expect_false_for_none_in_bounds(self):
        bounds = IntBounds(1, 2)
        self.assertTrue(bounds.are_valid())
        bounds.min = None
        self.assertFalse(bounds.are_valid())
        bounds.max = None
        self.assertFalse(bounds.are_valid())


class TestInvalidAttributeAndSkill(unittest.TestCase):
    def test_total_rating_bounds_expect_min_max_to_be_smaller_than_valid_min(self):
        for property_class, invalid_property in zip([Attribute, Skill],
                                                    [Attributes.INVALID.value, Skills.INVALID.value]):
            for val in invalid_property.rating_bounds:
                with self.subTest(i=f"{type(invalid_property).__name__}: {val}"):
                    self.assertFalse(property_class.is_valid_rating(val))
                    self.assertIsNone(val)

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
        for val in [Skill.rating_bounds.min, Skill.rating_bounds.max]:
            with self.subTest(i=val):
                self.assertFalse(Skills.INVALID.value.is_valid_total_rating(val))

class TestInvalidTrait(unittest.TestCase):
    def test_is_valid_rating_expect_false(self):
        tier = 1
        for val in Traits.Conviction.value.get_rating_bounds(related_tier=tier):
            with self.subTest(i=val):
                self.assertFalse(Traits.INVALID.value.is_valid_rating(val, related_tier=tier))