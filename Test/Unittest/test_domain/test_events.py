from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_positional_range, anon_name, anon_event, anon_id_prefix, anon_tag, anon_description, \
    anon_prefixed_id
from domain.descriptors import DescribedEntity, NamedEntity
from domain.events import Event
from domain.ids import IdentifiedEntity, generate_prefixed_id
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


class TestEvent(TestCase):
    def test__init__should_reject_ids_that_are_not_prefixed_with_event(self) -> None:
        # Arrange
        span = anon_positional_range()
        name = anon_name()
        description = anon_description()
        tags = {anon_tag()}

        # Act
        def action(): _ = Event(id=generate_prefixed_id(prefix=anon_id_prefix()), span=span, name=name, description=description, tags=tags)

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_initialize_traveler_ids_empty__when_no_ids_given(self) -> None:
        # Arrange
        event = Event(id=anon_prefixed_id(prefix="event"), name=anon_name(), span=anon_positional_range())

        # Act
        actual = event.affected_travelers

        # Assert
        self.assertSetEqual(set(), actual)

    def test__init__should_initialize_location_ids_empty__when_no_ids_given(self) -> None:
        # Arrange
        event = Event(id=anon_prefixed_id(prefix="event"), name=anon_name(), span=anon_positional_range())

        # Act
        actual = event.affected_locations

        # Assert
        self.assertSetEqual(set(), actual)

    def test__isinstance__should_be_named(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        actual = isinstance(event, NamedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_described(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        actual = isinstance(event, DescribedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_spanning(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        actual = isinstance(event, SpanningEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_identified(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        actual = isinstance(event, IdentifiedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_tagged(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        actual = isinstance(event, TaggedEntity)

        # Assert
        self.assertTrue(actual)

    def test__affected_travelers__should_not_allow_external_mutation(self) -> None:
        # Arrange
        event = anon_event()
        expected = frozenset(event.affected_travelers)

        # Act
        event.affected_travelers.add(anon_prefixed_id(prefix="traveler"))

        # Assert
        self.assertSetEqual(expected, event.affected_travelers)

    def test__affected_travelers__should_not_be_settable(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        def action():
            # noinspection PyPropertyAccess
            event.affected_travelers = set()

        # Assert
        self.assertRaises(AttributeError, action)

    def test__affected_locations__should_not_allow_external_mutation(self) -> None:
        # Arrange
        event = anon_event()
        expected = frozenset(event.affected_locations)

        # Act
        event.affected_locations.add(anon_prefixed_id(prefix="location"))

        # Assert
        self.assertSetEqual(expected, event.affected_locations)

    def test__affected_locations__should_not_be_settable(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        def action():
            # noinspection PyPropertyAccess
            event.affected_locations = set()

        # Assert
        self.assertRaises(AttributeError, action)

    def test__equality__should_correctly_compare_attributes(self) -> None:
        # Arrange
        location_id_1 = anon_prefixed_id(prefix="location")
        location_id_2 = anon_prefixed_id(prefix="location")
        traveler_id_1 = anon_prefixed_id(prefix="traveler")
        traveler_id_2 = anon_prefixed_id(prefix="traveler")
        event_id_1 = anon_prefixed_id(prefix="event")
        event_id_2 = anon_prefixed_id(prefix="event")
        name = anon_name()
        description = anon_description()
        span = anon_positional_range()
        event_a = Event(affected_locations={location_id_1}, affected_travelers={traveler_id_1}, id=event_id_1, name=name,
                        description=description, span=span)
        event_b = Event(affected_locations={location_id_1}, affected_travelers={traveler_id_1}, id=event_id_1, name=name,
                        description=description, span=span)
        event_c = Event(affected_locations={location_id_2}, affected_travelers={traveler_id_1}, id=event_id_1, name=name,
                        description=description, span=span)
        event_d = Event(affected_locations={location_id_1}, affected_travelers={traveler_id_2}, id=event_id_1, name=name,
                        description=description, span=span)
        event_e = Event(affected_locations={location_id_1}, affected_travelers={traveler_id_1}, id=event_id_2, name=name,
                        description=description, span=span)

        # Act
        actual_a_equals_b = event_a == event_b
        actual_a_not_equals_b = event_a != event_b
        actual_a_equals_c = event_a == event_c
        actual_a_not_equals_c = event_a != event_c
        actual_a_equals_d = event_a == event_d
        actual_a_not_equals_d = event_a != event_d
        actual_a_equals_e = event_a == event_e
        actual_a_not_equals_e = event_a != event_e

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        self.assertFalse(actual_a_equals_d)
        self.assertTrue(actual_a_not_equals_d)
        self.assertFalse(actual_a_equals_e)
        self.assertTrue(actual_a_not_equals_e)

    def test__hash__should_be_hashable__when_has_no_tags(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        def action(): _ = {event}

        # Assert
        action()
