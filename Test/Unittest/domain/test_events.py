from unittest import TestCase
from uuid import uuid4

from Test.Unittest.test_helpers.anons import anon_positional_range, anon_name, anon_event, anon_id_prefix, anon_tag, anon_description
from domain.descriptors import DescribedEntity, NamedEntity
from domain.events import Event
from domain.ids import PrefixedUUID, IdentifiedEntity
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
        def Action(): _ = Event(id=PrefixedUUID(prefix=anon_id_prefix(), uuid=uuid4()), span=span, name=name, description=description, tags=tags)

        # Assert
        self.assertRaises(ValueError, Action)

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
