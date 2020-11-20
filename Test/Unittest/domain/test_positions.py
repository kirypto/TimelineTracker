from random import choice
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_float, anon_int, anon_position, anon_positional_range, anon_range, anon_journey, anon_anything
from Test.Unittest.test_helpers.anons import anon_movement_type, \
    anon_positional_move
from domain.base_entity import BaseEntity
from domain.collections import Range
from domain.positions import Position, PositionalRange, SpanningEntity, JourneyingEntity, MovementType
from domain.positions import PositionalMove


# noinspection PyPropertyAccess
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

    def test__init__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = choice(["string", False, True])

        # Act
        def InvalidLatitude(): Position(latitude=invalid_type,
                                        longitude=anon_float(), altitude=anon_float(), continuum=anon_float(), reality=anon_int())

        def InvalidLongitude(): Position(longitude=invalid_type,
                                         latitude=anon_float(), altitude=anon_float(), continuum=anon_float(), reality=anon_int())

        def InvalidAltitude(): Position(altitude=invalid_type,
                                        latitude=anon_float(), longitude=anon_float(), continuum=anon_float(), reality=anon_int())

        def InvalidContinuum(): Position(continuum=invalid_type,
                                         latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), reality=anon_int())

        def InvalidReality(): Position(reality=invalid_type,
                                       latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), continuum=anon_float())

        # Assert
        self.assertRaises(TypeError, InvalidLatitude)
        self.assertRaises(TypeError, InvalidLongitude)
        self.assertRaises(TypeError, InvalidAltitude)
        self.assertRaises(TypeError, InvalidContinuum)
        self.assertRaises(TypeError, InvalidReality)

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

    def test__equality__should_compare_as_same__when_all_dimensions_are_equal(self) -> None:
        # Arrange
        def copy_and_set(dictionary, key, val):
            copy = dict(dictionary)
            copy[key] = val
            return copy

        kwargs = {
            "latitude": anon_float(),
            "longitude": anon_float(),
            "altitude": anon_float(),
            "continuum": anon_float(),
            "reality": anon_int(),
        }
        position_a = Position(**dict(kwargs))
        position_b = Position(**dict(kwargs))
        position_c = Position(**copy_and_set(kwargs, "latitude", anon_float()))
        position_d = Position(**copy_and_set(kwargs, "longitude", anon_float()))
        position_e = Position(**copy_and_set(kwargs, "altitude", anon_float()))
        position_f = Position(**copy_and_set(kwargs, "continuum", anon_float()))
        position_g = Position(**copy_and_set(kwargs, "reality", anon_int()))

        # Act
        actual_a_equals_b = position_a == position_b
        actual_a_not_equals_b = position_a != position_b
        actual_a_equals_c = position_a == position_c
        actual_a_not_equals_c = position_a != position_c
        actual_a_equals_d = position_a == position_d
        actual_a_not_equals_d = position_a != position_d
        actual_a_equals_e = position_a == position_e
        actual_a_not_equals_e = position_a != position_e
        actual_a_equals_f = position_a == position_f
        actual_a_not_equals_f = position_a != position_f
        actual_a_equals_g = position_a == position_g
        actual_a_not_equals_g = position_a != position_g

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        self.assertFalse(actual_a_equals_d)
        self.assertTrue(actual_a_not_equals_d)
        self.assertFalse(actual_a_equals_e)
        self.assertTrue(actual_a_not_equals_e)
        self.assertFalse(actual_a_equals_f)
        self.assertTrue(actual_a_not_equals_f)
        self.assertFalse(actual_a_equals_g)
        self.assertTrue(actual_a_not_equals_g)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        position = anon_position()

        # Act
        def Action(): _ = {position}

        # Assert
        Action()


# noinspection PyTypeChecker
class TestPositionalRange(TestCase):
    def test__init__should_initialize_from_provided_args(self) -> None:
        # Arrange
        expected_latitude = anon_range()
        expected_longitude = anon_range()
        expected_altitude = anon_range()
        expected_continuum = anon_range()
        expected_reality = anon_range(int)

        # Act
        actual = PositionalRange(latitude=expected_latitude, longitude=expected_longitude, altitude=expected_altitude, continuum=expected_continuum,
                                 reality=expected_reality)

        # Assert
        self.assertEqual(expected_latitude, actual.latitude)
        self.assertEqual(expected_longitude, actual.longitude)
        self.assertEqual(expected_altitude, actual.altitude)
        self.assertEqual(expected_continuum, actual.continuum)
        self.assertEqual(expected_reality, actual.reality)

    def test__init__should_support_kwargs(self) -> None:
        # Arrange
        class KwargsTest(PositionalRange, _Other):
            pass

        # Act
        actual = KwargsTest(latitude=anon_range(), longitude=anon_range(), altitude=anon_range(), continuum=anon_range(), reality=anon_range(int),
                            other="other")

        # Assert
        self.assertEqual("other", actual.other)

    def test__init__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = choice(["string", False, True])

        # Act
        def InvalidLatitude(): PositionalRange(latitude=invalid_type,
                                               longitude=anon_range(), altitude=anon_range(), continuum=anon_range(), reality=anon_range(int))

        def InvalidLongitude(): PositionalRange(longitude=invalid_type,
                                                latitude=anon_range(), altitude=anon_range(), continuum=anon_range(), reality=anon_range(int))

        def InvalidAltitude(): PositionalRange(altitude=invalid_type,
                                               latitude=anon_range(), longitude=anon_range(), continuum=anon_range(), reality=anon_range(int))

        def InvalidContinuum(): PositionalRange(continuum=invalid_type,
                                                latitude=anon_range(), longitude=anon_range(), altitude=anon_range(), reality=anon_range(int))

        def InvalidReality(): PositionalRange(reality=invalid_type,
                                              latitude=anon_range(), longitude=anon_range(), altitude=anon_range(), continuum=anon_range())

        # Assert
        self.assertRaises(TypeError, InvalidLatitude)
        self.assertRaises(TypeError, InvalidLongitude)
        self.assertRaises(TypeError, InvalidAltitude)
        self.assertRaises(TypeError, InvalidContinuum)
        self.assertRaises(TypeError, InvalidReality)

    def test__includes__should_return_true__when_provided_position_is_within_positional_range(self) -> None:
        # Arrange
        low = anon_int()
        high = low + abs(anon_int())
        within = anon_float(low, high)
        range_ = Range(low=low, high=high)
        positional_range = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality=range_)
        position = Position(latitude=low, longitude=high, altitude=within, continuum=within, reality=anon_int(low, high))

        # Act
        actual = positional_range.includes(position)

        # Assert
        self.assertTrue(actual)

    def test__includes__should_return_false__when_any_dimension_of_provided_position_is_outside_range(self) -> None:
        # Arrange
        low = anon_int()
        high = low + abs(anon_int())
        range_ = Range(low=low, high=high)
        positional_range = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality=range_)
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

    def test__includes__should_reject_non_position_arguments(self) -> None:
        # Arrange
        low = anon_int()
        high = low + abs(anon_int())
        range_ = Range(low=low, high=high)
        positional_range = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality=range_)
        invalid_type = choice([True, 1.0, "nope", positional_range])

        # Act
        def Action(): positional_range.includes(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__intersects__should_return_true__when_provided_range_partially_overlaps(self) -> None:
        # Arrange
        low = anon_int()
        high = low + abs(anon_int())
        range_ = Range(low=low, high=high)
        positional_range = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality=range_)
        other = PositionalRange(latitude=Range(low=high, high=high + 1),
                                longitude=Range(low=low - 1, high=low),
                                altitude=Range(low=high - 1, high=high + 1),
                                continuum=Range(low=low - 1, high=low + 1),
                                reality=Range(low=low - 1, high=high + 1))

        # Act
        actual = positional_range.intersects(other)

        # Assert
        self.assertTrue(actual)

    def test__intersects__should_return_true__when_provided_range_contained_completely(self) -> None:
        # Arrange
        low = anon_int()
        high = low + abs(anon_int())
        range_ = Range(low=low, high=high)
        positional_range = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality=range_)
        other = PositionalRange(latitude=Range(low=low + 1, high=high - 1),
                                longitude=Range(low=low + 1, high=high - 1),
                                altitude=Range(low=low + 1, high=high - 1),
                                continuum=Range(low=low + 1, high=high - 1),
                                reality=Range(low=low + 1, high=high - 1))

        # Act
        actual = positional_range.intersects(other)

        # Assert
        self.assertTrue(actual)

    def test__intersects__should_return_false__when_provided_range_does_not_overlap(self) -> None:
        # Arrange
        low = anon_int()
        high = low + abs(anon_int())
        range_ = Range(low=low, high=high)
        positional_range = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality=range_)
        out_of_bound_ranges = [Range(low=low - abs(anon_int()), high=low - 1), Range(low=high + 1, high=high + abs(anon_int()))]
        out_of_range_latitude = PositionalRange(latitude=choice(out_of_bound_ranges),
                                                longitude=range_, altitude=range_, continuum=range_, reality=range_)
        out_of_range_longitude = PositionalRange(longitude=choice(out_of_bound_ranges),
                                                 altitude=range_, continuum=range_, reality=range_, latitude=range_)
        out_of_range_altitude = PositionalRange(altitude=choice(out_of_bound_ranges),
                                                latitude=range_, longitude=range_, continuum=range_, reality=range_)
        out_of_range_continuum = PositionalRange(continuum=choice(out_of_bound_ranges),
                                                 latitude=range_, longitude=range_, altitude=range_, reality=range_)
        out_of_range_reality = PositionalRange(reality=choice(out_of_bound_ranges),
                                               latitude=range_, longitude=range_, altitude=range_, continuum=range_)

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

    def test__intersects__should_reject_non_positional_range_arguments(self) -> None:
        # Arrange
        positional_range = anon_positional_range()
        position = anon_position()
        invalid_type = choice([True, 1.0, "nope", position])

        # Act
        def Action(): positional_range.intersects(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__equality__should_compare_as_same__when_all_dimensions_are_equal(self) -> None:
        # Arrange
        def copy_and_set(dictionary, key, val):
            copy = dict(dictionary)
            copy[key] = val
            return copy

        kwargs = {
            "latitude": anon_range(),
            "longitude": anon_range(),
            "altitude": anon_range(),
            "continuum": anon_range(),
            "reality": anon_range(int),
        }
        position_a = PositionalRange(**dict(kwargs))
        position_b = PositionalRange(**dict(kwargs))
        position_c = PositionalRange(**copy_and_set(kwargs, "latitude", anon_range()))
        position_d = PositionalRange(**copy_and_set(kwargs, "longitude", anon_range()))
        position_e = PositionalRange(**copy_and_set(kwargs, "altitude", anon_range()))
        position_f = PositionalRange(**copy_and_set(kwargs, "continuum", anon_range()))
        position_g = PositionalRange(**copy_and_set(kwargs, "reality", anon_range(int)))

        # Act
        actual_a_equals_b = position_a == position_b
        actual_a_not_equals_b = position_a != position_b
        actual_a_equals_c = position_a == position_c
        actual_a_not_equals_c = position_a != position_c
        actual_a_equals_d = position_a == position_d
        actual_a_not_equals_d = position_a != position_d
        actual_a_equals_e = position_a == position_e
        actual_a_not_equals_e = position_a != position_e
        actual_a_equals_f = position_a == position_f
        actual_a_not_equals_f = position_a != position_f
        actual_a_equals_g = position_a == position_g
        actual_a_not_equals_g = position_a != position_g

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        self.assertFalse(actual_a_equals_d)
        self.assertTrue(actual_a_not_equals_d)
        self.assertFalse(actual_a_equals_e)
        self.assertTrue(actual_a_not_equals_e)
        self.assertFalse(actual_a_equals_f)
        self.assertTrue(actual_a_not_equals_f)
        self.assertFalse(actual_a_equals_g)
        self.assertTrue(actual_a_not_equals_g)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        positional_range = anon_positional_range()

        # Act
        def Action(): _ = {positional_range}

        # Assert
        Action()


# noinspection PyTypeChecker
class TestPositionalMove(TestCase):
    def test__init__should_initialize_from_provided_args(self) -> None:
        # Arrange
        expected_position = anon_position()
        expected_movement_type = anon_movement_type()

        # Act
        actual = PositionalMove(position=expected_position, movement_type=expected_movement_type)

        # Assert
        self.assertEqual(expected_position, actual.position)
        self.assertEqual(expected_movement_type, actual.movement_type)

    def test__init__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = choice(["string", False, True])

        # Act
        def InvalidPosition(): PositionalMove(position=invalid_type, movement_type=anon_movement_type())

        def InvalidMovementType(): PositionalMove(movement_type=invalid_type, position=anon_position())

        # Assert
        self.assertRaises(TypeError, InvalidPosition)
        self.assertRaises(TypeError, InvalidMovementType)

    def test__equality__should_compare_as_same__when_all_attributes_are_equal(self) -> None:
        # Arrange
        def copy_and_set(dictionary, key, val):
            copy = dict(dictionary)
            copy[key] = val
            return copy

        movement_type = anon_movement_type()
        other_movement_type = choice([type_ for type_ in MovementType if type_ != movement_type])
        kwargs = {
            "position": anon_position(),
            "movement_type": movement_type,
        }
        positional_move_a = PositionalMove(**dict(kwargs))
        positional_move_b = PositionalMove(**dict(kwargs))
        positional_move_c = PositionalMove(**copy_and_set(kwargs, "position", anon_position()))
        positional_move_d = PositionalMove(**copy_and_set(kwargs, "movement_type", other_movement_type))

        # Act
        actual_a_equals_b = positional_move_a == positional_move_b
        actual_a_not_equals_b = positional_move_a != positional_move_b
        actual_a_equals_c = positional_move_a == positional_move_c
        actual_a_not_equals_c = positional_move_a != positional_move_c
        actual_a_equals_d = positional_move_a == positional_move_d
        actual_a_not_equals_d = positional_move_a != positional_move_d

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        self.assertFalse(actual_a_equals_d)
        self.assertTrue(actual_a_not_equals_d)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        positional_move = anon_positional_move()

        # Act
        def Action(): _ = {positional_move}

        # Assert
        Action()


# noinspection PyPropertyAccess
class TestSpanningEntity(TestCase):
    def test__init__should_initialize_with_provided_value(self) -> None:
        # Arrange
        expected = anon_positional_range()

        # Act
        actual = SpanningEntity(span=expected)

        # Assert
        self.assertEqual(expected, actual.span)

    def test__init__reject_invalid_typed_span(self) -> None:
        # Arrange
        illegal_type = choice([1, True, "nope"])

        # Act
        def Action(): SpanningEntity(span=illegal_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__init__should_accept_kwargs(self) -> None:
        # Arrange
        class TestKwargs(SpanningEntity, _Other):
            pass

        # Act
        expected = "other"

        def Action(): return TestKwargs(span=anon_positional_range(), other=expected)

        actual = Action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__description__should_not_be_mutable(self) -> None:
        # Arrange
        spanning_entity = SpanningEntity(span=anon_positional_range())

        # Act
        def Action(): spanning_entity.span = anon_positional_range()

        # Assert
        self.assertRaises(AttributeError, Action)

    def test__equality__should_correctly_compare_span(self) -> None:
        # Arrange
        positional_range_1 = anon_positional_range()
        positional_range_2 = anon_positional_range()
        spanning_entity_a = SpanningEntity(span=positional_range_1)
        spanning_entity_b = SpanningEntity(span=positional_range_1)
        spanning_entity_c = SpanningEntity(span=positional_range_2)

        # Act
        actual_a_equals_b = spanning_entity_a == spanning_entity_b
        actual_a_not_equals_b = spanning_entity_a != spanning_entity_b
        actual_a_equals_c = spanning_entity_a == spanning_entity_c
        actual_a_not_equals_c = spanning_entity_a != spanning_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        spanning_entity = SpanningEntity(span=anon_positional_range())

        # Act
        def Action(): _ = {spanning_entity}

        # Assert
        Action()


# noinspection PyPropertyAccess
class TestJourneyingEntity(TestCase):
    def test__init__should_initialize_with_provided_value(self) -> None:
        # Arrange
        expected = anon_journey()

        # Act
        actual = JourneyingEntity(journey=expected)

        # Assert
        self.assertEqual(expected, actual.journey)

    def test__init__reject_invalid_typed_args(self) -> None:
        # Arrange
        illegal_type = anon_anything()

        # Act
        def Action(): JourneyingEntity(journey=illegal_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__init__should_accept_kwargs(self) -> None:
        # Arrange
        class TestKwargs(JourneyingEntity, _Other):
            pass

        # Act
        expected = "other"

        def Action(): return TestKwargs(journey=anon_journey(), other=expected)

        actual = Action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__journey__should_not_be_mutable(self) -> None:
        # Arrange
        spanning_entity = JourneyingEntity(journey=anon_journey())

        # Act
        def Action(): spanning_entity.journey = anon_journey()

        # Assert
        self.assertRaises(AttributeError, Action)

    def test__equality__should_correctly_compare_attributes(self) -> None:
        # Arrange
        journey_1 = anon_journey()
        journey_2 = anon_journey()
        journeying_entity_a = JourneyingEntity(journey=journey_1)
        journeying_entity_b = JourneyingEntity(journey=journey_1)
        journeying_entity_c = JourneyingEntity(journey=journey_2)

        # Act
        actual_a_equals_b = journeying_entity_a == journeying_entity_b
        actual_a_not_equals_b = journeying_entity_a != journeying_entity_b
        actual_a_equals_c = journeying_entity_a == journeying_entity_c
        actual_a_not_equals_c = journeying_entity_a != journeying_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        journeying_entity = JourneyingEntity(journey=anon_journey())

        # Act
        def Action(): _ = {journeying_entity}

        # Assert
        Action()


class _Other(BaseEntity):
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
