from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_name, anon_description, anon_id_prefix, anon_traveler, anon_positional_range, anon_tag
from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, generate_prefixed_id
from domain.positions import JourneyingEntity
from domain.tags import TaggedEntity
from domain.travelers import Traveler


class TestTraveler(TestCase):
    def test__init__should_reject_ids_that_are_not_prefixed_with_traveler(self) -> None:
        # Arrange
        span = anon_positional_range()
        name = anon_name()
        description = anon_description()
        tags = {anon_tag()}

        # Act
        def action(): _ = Traveler(id=generate_prefixed_id(prefix=anon_id_prefix()), span=span, name=name, description=description,
                                   tags=tags)

        # Assert
        self.assertRaises(ValueError, action)

    def test__isinstance__should_be_named(self) -> None:
        # Arrange
        traveler = anon_traveler()

        # Act
        actual = isinstance(traveler, NamedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_described(self) -> None:
        # Arrange
        traveler = anon_traveler()

        # Act
        actual = isinstance(traveler, DescribedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_journeying(self) -> None:
        # Arrange
        traveler = anon_traveler()

        # Act
        actual = isinstance(traveler, JourneyingEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_identified(self) -> None:
        # Arrange
        traveler = anon_traveler()

        # Act
        actual = isinstance(traveler, IdentifiedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_tagged(self) -> None:
        # Arrange
        traveler = anon_traveler()

        # Act
        actual = isinstance(traveler, TaggedEntity)

        # Assert
        self.assertTrue(actual)
