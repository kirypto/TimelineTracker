from random import choice
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_float, anon_range
from domain.collections import Range


class TestRange(TestCase):
    def test__init__should_initialize_from_provided_args(self) -> None:
        # Arrange
        expected_low = anon_float()
        expected_high = expected_low + abs(anon_float())

        # Act
        actual = Range(low=expected_low, high=expected_high)

        # Assert
        self.assertEqual(expected_low, actual.low)
        self.assertEqual(expected_high, actual.high)

    def test__init__should_reject_when_low_and_high_args_are_of_different_types(self) -> None:
        # Arrange
        non_float_type = choice(["string", False, True, 0])

        # Act
        def DifferentTypeLow(): Range(low=non_float_type, high=anon_float())

        def DifferentTypeHigh(): Range(low=anon_float(), high=non_float_type)

        # Assert
        self.assertRaises(TypeError, DifferentTypeLow)
        self.assertRaises(TypeError, DifferentTypeHigh)

    def test__init__should_reject_low_values_greater_than_high(self) -> None:
        # Arrange
        low = anon_float()
        high = low - abs(anon_float())

        # Act
        def Action(): Range(low=low, high=high)

        # Assert
        self.assertRaises(ValueError, Action)

    def test__properties__should_not_be_mutable(self) -> None:
        # Arrange
        range_ = anon_range()

        # Act
        def ActionLow(): range_.low = anon_float()

        def ActionHigh(): range_.high = anon_float()

        # Assert
        self.assertRaises(AttributeError, ActionLow)
        self.assertRaises(AttributeError, ActionHigh)

    def test__includes__should_reject_arguments_of_invalid_types(self) -> None:
        # Arrange
        invalid_type = choice(["string", False, True])
        range_ = anon_range(float)

        # Act
        def Action(): range_.includes(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__includes__should_return_true__when_value_is_within_range(self) -> None:
        # Arrange
        range_ = anon_range()
        query_val = anon_float(range_.low + 0.1, range_.high - 0.1)

        # Act
        actual = range_.includes(query_val)

        # Assert
        self.assertTrue(actual)

    def test__includes__should_return_true__when_value_is_equal_to_either_range_end(self) -> None:
        # Arrange
        range_ = anon_range()

        # Act
        actual_low = range_.includes(float(range_._low))
        actual_high = range_.includes(float(range_._high))

        # Assert
        self.assertTrue(actual_low)
        self.assertTrue(actual_high)

    def test__includes__should_return_false__when_value_is_above_or_below_range(self) -> None:
        # Arrange
        range_ = anon_range()
        query_val_below = range_.low - abs(anon_float())
        query_val_above = range_.low - abs(anon_float())

        # Act
        actual_below = range_.includes(query_val_below)
        actual_above = range_.includes(query_val_above)

        # Assert
        self.assertFalse(actual_below)
        self.assertFalse(actual_above)

    def test__intersects__should_reject_arguments_of_invalid_types(self) -> None:
        # Arrange
        invalid_type = choice(["string", False, True, anon_float()])
        range_ = anon_range(float)

        # Act
        def Action(): range_.intersects(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__intersects__should_return_true__when_provided_range_partially_overlaps(self) -> None:
        # Arrange
        range_ = anon_range()
        overlap_low = Range(low=range_.low - abs(anon_float()), high=range_.low + abs(anon_float()))
        overlap_high = Range(low=range_.high - abs(anon_float()), high=range_.high + abs(anon_float()))

        # Act
        actual_low = range_.intersects(overlap_low)
        actual_high = range_.intersects(overlap_high)

        # Assert
        self.assertTrue(actual_low)
        self.assertTrue(actual_high)

    def test__intersects__should_return_true__when_provided_range_is_contiguous(self) -> None:
        # Arrange
        range_ = anon_range()
        contiguous_low = Range(low=range_.low - abs(anon_float()), high=range_.low)
        contiguous_high = Range(low=range_.high - abs(anon_float()), high=range_.high)

        # Act
        actual_low = range_.intersects(contiguous_low)
        actual_high = range_.intersects(contiguous_high)

        # Assert
        self.assertTrue(actual_low)
        self.assertTrue(actual_high)

    def test__intersects__should_return_true__when_provided_range_contained_completely(self) -> None:
        # Arrange
        range_ = anon_range()
        contained_range = Range(low=range_.low + 0.1, high=range_.high - 0.1)

        # Act
        actual = range_.intersects(contained_range)

        # Assert
        self.assertTrue(actual)

    def test__intersects__should_return_false__when_provided_range_does_not_overlap(self) -> None:
        # Arrange
        range_ = anon_range()
        out_of_range_below = Range(low=range_.low - abs(anon_float()), high=range_.low - 0.1)
        out_of_range_above = Range(low=range_.high + 0.1, high=range_.high + abs(anon_float()))

        # Act
        actual_below = range_.intersects(out_of_range_below)
        actual_above = range_.intersects(out_of_range_above)

        # Assert
        self.assertFalse(actual_below)
        self.assertFalse(actual_above)

    def test__equality__should_compare_as_same__when_provided_range_is_equal(self) -> None:
        # Arrange
        low = anon_float()
        high = low + abs(anon_float())
        position_a = Range(low=low, high=high)
        position_b = Range(low=low, high=high)
        position_c = Range(low=low, high=high + abs(anon_float()))
        position_d = Range(low=low - abs(anon_float()), high=high)

        # Act
        actual_a_equals_b = position_a == position_b
        actual_a_not_equals_b = position_a != position_b
        actual_a_equals_c = position_a == position_c
        actual_a_not_equals_c = position_a != position_c
        actual_a_equals_d = position_a == position_d
        actual_a_not_equals_d = position_a != position_d

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        self.assertFalse(actual_a_equals_d)
        self.assertTrue(actual_a_not_equals_d)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        position = anon_range()

        # Act
        def Action(): _ = {position}

        # Assert
        Action()
