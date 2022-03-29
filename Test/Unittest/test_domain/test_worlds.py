from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_name, anon_description, anon_id_prefix, anon_positional_range, anon_tag, anon_world
from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, generate_prefixed_id
from domain.tags import TaggedEntity
from domain.worlds import World


class TestWorld(TestCase):
    def test__init__should_reject_ids_that_are_not_prefixed_with_world(self) -> None:
        # Arrange
        span = anon_positional_range()
        name = anon_name()
        description = anon_description()
        tags = {anon_tag()}

        # Act
        def action(): _ = World(id=generate_prefixed_id(anon_id_prefix()), span=span, name=name, description=description, tags=tags)

        # Assert
        self.assertRaises(ValueError, action)

    def test__isinstance__should_be_named(self) -> None:
        # Arrange
        world = anon_world()

        # Act
        actual = isinstance(world, NamedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_described(self) -> None:
        # Arrange
        world = anon_world()

        # Act
        actual = isinstance(world, DescribedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_identified(self) -> None:
        # Arrange
        world = anon_world()

        # Act
        actual = isinstance(world, IdentifiedEntity)

        # Assert
        self.assertTrue(actual)

    def test__isinstance__should_be_tagged(self) -> None:
        # Arrange
        world = anon_world()

        # Act
        actual = isinstance(world, TaggedEntity)

        # Assert
        self.assertTrue(actual)
