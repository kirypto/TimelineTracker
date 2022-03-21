from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_name, anon_description, anon_id_prefix, anon_location, anon_positional_range, anon_tag
from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, generate_prefixed_id
from domain.locations import Location
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


class TestLocation(TestCase):
    def test__init__should_reject_ids_that_are_not_prefixed_with_location(self) -> None:
        # Arrange
        span = anon_positional_range()
        name = anon_name()
        description = anon_description()
        tags = {anon_tag()}

        # Act
        def action(): _ = Location(id=generate_prefixed_id(anon_id_prefix()), span=span, name=name, description=description, tags=tags)

        # Assert
        self.assertRaises(ValueError, action)

    def test__isinstance__should_be_named(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = isinstance(location, NamedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_described(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = isinstance(location, DescribedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_spanning(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = isinstance(location, SpanningEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_identified(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = isinstance(location, IdentifiedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_tagged(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = isinstance(location, TaggedEntity)

        # Assert
        self.assertTrue(actual)
