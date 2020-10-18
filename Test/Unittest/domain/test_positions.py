from random import choice, randint, uniform
from unittest import TestCase

from domain.positions import Position, PositionalRange


def anon_float(a: float = None, b: float = None):
    start = a if a is not None else -999999.9
    end = b if b is not None else 999999.9
    return uniform(start, end)


def anon_int(a: int = None, b: int = None):
    start = a if a is not None else -999999
    end = b if b is not None else 999999
    return randint(start, end)


class TestPosition(TestCase):
    def test__init__should_initialize_from_provided_args(self) -> None:
        # Arrange
        expected_latitude = anon_float()
        expected_longitude = anon_float()
        expected_altitude = anon_float()
        expected_continuum = anon_float()
        expected_reality = anon_int()

        # Act
        actual = Position(latitude=expected_latitude, longitude=expected_longitude, altitude=expected_altitude, continuum=expected_continuum,
                          reality=expected_reality)

        # Assert
        self.assertEqual(expected_latitude, actual.latitude)
        self.assertEqual(expected_longitude, actual.longitude)
        self.assertEqual(expected_altitude, actual.altitude)
        self.assertEqual(expected_continuum, actual.continuum)
        self.assertEqual(expected_reality, actual.reality)

    def test__init__should_support_kwargs(self) -> None:
        # Arrange
        class KwargsTest(Position, _Other):
            pass

        # Act
        actual = KwargsTest(latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), continuum=anon_float(), reality=anon_int(),
                            other="other")

        # Assert
        self.assertEqual("other", actual.other)

    def test__properties__should_not_be_mutable(self) -> None:
        # Arrange
        position = Position(latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), continuum=anon_float(), reality=anon_int())

        # Act
        def ActionLatitude(): position.latitude = anon_float()

        def ActionLongitude(): position.longitude = anon_float()

        def ActionAltitude(): position.altitude = anon_float()

        def ActionContinuum(): position.continuum = anon_float()

        def ActionReality(): position.reality = anon_float()

        # Assert
        self.assertRaises(AttributeError, ActionLatitude)
        self.assertRaises(AttributeError, ActionLongitude)
        self.assertRaises(AttributeError, ActionAltitude)
        self.assertRaises(AttributeError, ActionContinuum)
        self.assertRaises(AttributeError, ActionReality)


class TestPositionalRange(TestCase):
    def test__init__should_initialize_from_provided_singular_args(self) -> None:
        # Arrange
        expected_latitude = anon_float()
        expected_longitude = anon_float()
        expected_altitude = anon_float()
        expected_continuum = anon_float()
        expected_reality = anon_int()

        # Act
        actual = PositionalRange(latitude=expected_latitude, longitude=expected_longitude, altitude=expected_altitude, continuum=expected_continuum,
                                 reality=expected_reality)

        # Assert
        self.assertEqual(expected_latitude, actual.latitude_low)
        self.assertEqual(expected_latitude, actual.latitude_high)
        self.assertEqual(expected_longitude, actual.longitude_low)
        self.assertEqual(expected_longitude, actual.longitude_high)
        self.assertEqual(expected_altitude, actual.altitude_low)
        self.assertEqual(expected_altitude, actual.altitude_high)
        self.assertEqual(expected_continuum, actual.continuum_low)
        self.assertEqual(expected_continuum, actual.continuum_high)
        self.assertEqual(expected_reality, actual.reality_low)
        self.assertEqual(expected_reality, actual.reality_high)

    def test__init__should_initialize_from_provided_range_args(self) -> None:
        # Arrange
        expected_latitude_low = anon_float()
        expected_latitude_high = anon_float()
        expected_longitude_low = anon_float()
        expected_longitude_high = anon_float()
        expected_altitude_low = anon_float()
        expected_altitude_high = anon_float()
        expected_continuum_low = anon_float()
        expected_continuum_high = anon_float()
        expected_reality_low = anon_int()
        expected_reality_high = anon_int()

        # Act
        actual = PositionalRange(latitude_low=expected_latitude_low, latitude_high=expected_latitude_high,
                                 longitude_low=expected_longitude_low, longitude_high=expected_longitude_high,
                                 altitude_low=expected_altitude_low, altitude_high=expected_altitude_high,
                                 continuum_low=expected_continuum_low, continuum_high=expected_continuum_high,
                                 reality_low=expected_reality_low, reality_high=expected_reality_high)

        # Assert
        self.assertEqual(expected_latitude_low, actual.latitude_low)
        self.assertEqual(expected_latitude_high, actual.latitude_high)
        self.assertEqual(expected_longitude_low, actual.longitude_low)
        self.assertEqual(expected_longitude_high, actual.longitude_high)
        self.assertEqual(expected_altitude_low, actual.altitude_low)
        self.assertEqual(expected_altitude_high, actual.altitude_high)
        self.assertEqual(expected_continuum_low, actual.continuum_low)
        self.assertEqual(expected_continuum_high, actual.continuum_high)
        self.assertEqual(expected_reality_low, actual.reality_low)
        self.assertEqual(expected_reality_high, actual.reality_high)

    def test__init__should_support_kwargs(self) -> None:
        # Arrange
        class KwargsTest(PositionalRange, _Other):
            pass

        # Act
        actual = KwargsTest(latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), continuum=anon_float(), reality=anon_int(),
                            other="other")

        # Assert
        self.assertEqual("other", actual.other)

    def test__includes__should_return_true__when_provided_position_is_within_positional_range(self) -> None:
        # Arrange
        low = anon_int()
        high = low + anon_int()
        positional_range = PositionalRange(latitude_low=low, latitude_high=high,
                                           longitude_low=low, longitude_high=high,
                                           altitude_low=low, altitude_high=high,
                                           continuum_low=low, continuum_high=high,
                                           reality_low=low, reality_high=high)
        position = Position(latitude=low, longitude=high, altitude=anon_float(low, high), continuum=anon_float(low, high),
                            reality=anon_int(low, high))

        # Act
        actual = positional_range.includes(position)

        # Assert
        self.assertTrue(actual)

    def test__includes__should_return_false__when_any_dimension_of_provided_position_is_outside_range(self) -> None:
        # Arrange
        low = anon_int()
        high = low + anon_int()
        positional_range = PositionalRange(latitude_low=low, latitude_high=high,
                                           longitude_low=low, longitude_high=high,
                                           altitude_low=low, altitude_high=high,
                                           continuum_low=low, continuum_high=high,
                                           reality_low=low, reality_high=high)
        out_of_range_values = [low - 1, high + 1]
        out_of_range_latitude = Position(latitude=choice(out_of_range_values), longitude=low, altitude=low, continuum=low, reality=low)
        out_of_range_longitude = Position(latitude=low, longitude=choice(out_of_range_values), altitude=low, continuum=low, reality=low)
        out_of_range_altitude = Position(latitude=low, longitude=low, altitude=choice(out_of_range_values), continuum=low, reality=low)
        out_of_range_continuum = Position(latitude=low, longitude=low, altitude=low, continuum=choice(out_of_range_values), reality=low)
        out_of_range_reality = Position(latitude=low, longitude=low, altitude=low, continuum=low, reality=choice(out_of_range_values))

        # Act
        actual_latitude = positional_range.includes(out_of_range_latitude)
        actual_longitude = positional_range.includes(out_of_range_longitude)
        actual_altitude = positional_range.includes(out_of_range_altitude)
        actual_continuum = positional_range.includes(out_of_range_continuum)
        actual_reality = positional_range.includes(out_of_range_reality)

        # Assert
        self.assertFalse(actual_latitude)
        self.assertFalse(actual_longitude)
        self.assertFalse(actual_altitude)
        self.assertFalse(actual_continuum)
        self.assertFalse(actual_reality)

    def test__intersects__should_return_true__when_provided_range_partially_overlaps(self) -> None:
        # Arrange
        low = anon_int()
        high = low + anon_int()
        positional_range = PositionalRange(latitude_low=low, latitude_high=high,
                                           longitude_low=low, longitude_high=high,
                                           altitude_low=low, altitude_high=high,
                                           continuum_low=low, continuum_high=high,
                                           reality_low=low, reality_high=high)
        other = PositionalRange(latitude_low=high, latitude_high=high + 1,
                                longitude_low=low - 1, longitude_high=low,
                                altitude_low=high - 1, altitude_high=high + 1,
                                continuum_low=low - 1, continuum_high=low + 1,
                                reality_low=low - 1, reality_high=high + 1)

        # Act
        actual = positional_range.intersects(other)

    def test__intersects__should_return_true__when_provided_range_contained_completely(self) -> None:
        # Arrange
        low = anon_int()
        high = low + 5
        positional_range = PositionalRange(latitude_low=low, latitude_high=high,
                                           longitude_low=low, longitude_high=high,
                                           altitude_low=low, altitude_high=high,
                                           continuum_low=low, continuum_high=high,
                                           reality_low=low, reality_high=high)
        other = PositionalRange(latitude_low=low + 1, latitude_high=high - 1,
                                longitude_low=low + 1, longitude_high=high - 1,
                                altitude_low=low + 1, altitude_high=high - 1,
                                continuum_low=low + 1, continuum_high=high - 1,
                                reality_low=low + 1, reality_high=high - 1)

        # Act
        actual = positional_range.intersects(other)

        # Assert
        self.assertTrue(actual)

    def test__intersects__should_return_false__when_provided_range_does_not_overlap(self) -> None:
        # Arrange
        low = anon_int()
        high = low + anon_int()
        positional_range = PositionalRange(latitude_low=low, latitude_high=high,
                                           longitude_low=low, longitude_high=high,
                                           altitude_low=low, altitude_high=high,
                                           continuum_low=low, continuum_high=high,
                                           reality_low=low, reality_high=high)
        out_of_range_values = [low - 1, high + 1]
        out_of_range_latitude = Position(latitude=choice(out_of_range_values), longitude=low, altitude=low, continuum=low, reality=low)
        out_of_range_longitude = Position(latitude=low, longitude=choice(out_of_range_values), altitude=low, continuum=low, reality=low)
        out_of_range_altitude = Position(latitude=low, longitude=low, altitude=choice(out_of_range_values), continuum=low, reality=low)
        out_of_range_continuum = Position(latitude=low, longitude=low, altitude=low, continuum=choice(out_of_range_values), reality=low)
        out_of_range_reality = Position(latitude=low, longitude=low, altitude=low, continuum=low, reality=choice(out_of_range_values))

        # Act
        actual_latitude = positional_range.intersects(out_of_range_latitude)
        actual_longitude = positional_range.intersects(out_of_range_longitude)
        actual_altitude = positional_range.intersects(out_of_range_altitude)
        actual_continuum = positional_range.intersects(out_of_range_continuum)
        actual_reality = positional_range.intersects(out_of_range_reality)

        # Assert
        self.assertFalse(actual_latitude)
        self.assertFalse(actual_longitude)
        self.assertFalse(actual_altitude)
        self.assertFalse(actual_continuum)
        self.assertFalse(actual_reality)


class _Other:
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
