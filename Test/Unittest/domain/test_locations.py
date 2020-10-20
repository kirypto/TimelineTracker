from unittest import TestCase
from uuid import uuid4

from Test.Unittest.domain.test_descriptors import anon_name, anon_description
from Test.Unittest.domain.test_ids import anon_id_prefix
from Test.Unittest.domain.test_positions import anon_positional_range
from Test.Unittest.domain.test_tags import anon_tag
from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


def anon_location() -> Location:
    return Location(id=PrefixedUUID(prefix="location", uuid=uuid4()),
                    span=anon_positional_range(),
                    name=anon_name(),
                    description=anon_description(),
                    tags={anon_tag()})


class TestLocation(TestCase):
    def test__init__should_reject_ids_that_are_not_prefixed_with_location(self) -> None:
        # Arrange
        span = anon_positional_range()
        name = anon_name()
        description = anon_description()
        tags = {anon_tag()}

        # Act
        def Action(): _ = Location(id=PrefixedUUID(prefix=anon_id_prefix(), uuid=uuid4()), span=span, name=name, description=description, tags=tags)

        # Assert
        self.assertRaises(ValueError, Action)

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
