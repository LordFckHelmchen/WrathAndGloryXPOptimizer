import unittest

from src.wrath_and_glory_xp_optimizer.character_properties import IntBounds
from wrath_and_glory_xp_optimizer.optimizer_results import XPCost


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

    def test_constructor_with_out_of_order_limits_expect_ordered_bounds(self):
        min_val = 7
        max_val = 100
        bounds = IntBounds(max_val, min_val)
        self.assertEqual(min_val, bounds.min)
        self.assertEqual(max_val, bounds.max)

    def test_scalar_add_expect_correct_results(self):
        min_val = -56
        max_val = -2
        add_val = 5
        expected_bounds = IntBounds(min_val + add_val, max_val + add_val)
        observed_bounds = IntBounds(min_val, max_val) + add_val
        self.assertEqual(expected_bounds, observed_bounds)

    def test_add_expect_correct_results(self):
        min_val = -7
        max_val = 236
        add_bounds = IntBounds(-3, 5)
        expected_bounds = IntBounds(min_val + add_bounds.min, max_val + add_bounds.max)
        observed_bounds = IntBounds(min_val, max_val) + add_bounds
        self.assertEqual(expected_bounds, observed_bounds)


class TestXPCost(unittest.TestCase):
    def test_Total_setter_expect_IOError_if_sum_is_incorrect(self):
        attribute_costs = 1
        skill_costs = 2
        total_costs = attribute_costs + skill_costs
        self.assertEqual(total_costs, XPCost(attribute_costs, skill_costs, total_costs).Total)
        self.assertEqual(total_costs, XPCost(attribute_costs, skill_costs).Total)  # Should not throw
        with self.assertRaises(IOError):
            XPCost(attribute_costs, skill_costs, total_costs + 1)


if __name__ == '__main__':
    unittest.main()
