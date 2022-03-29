from unittest import TestCase
from unittest.mock import patch, MagicMock

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_name, anon_description, anon_tag, anon_create_world_kwargs, \
    anon_world, anon_anything, anon_attributes
from application.access.clients import Profile
from application.use_case.world_use_cases import WorldUseCase
from domain.worlds import World


class TestWorldUseCase(TestCase):
    world_use_case: WorldUseCase
    profile: Profile

    def setUp(self) -> None:
        self.world_use_case = WorldUseCase()
        self.profile = Profile(anon_name(), anon_name())

    def test__create__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        world = self.world_use_case.create(name=anon_name(), profile=self.profile)

        # Assert
        self.assertTrue(hasattr(world, "id"))

    def test__create__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        world = self.world_use_case.create(id=undesired_id, name=anon_name(), profile=self.profile)

        # Assert
        self.assertNotEqual(undesired_id, world.id)

    def test__create__should_use_provided_args(self) -> None:
        # Arrange
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag()}
        expected_attributes = anon_attributes()

        # Act
        world = self.world_use_case.create(
            name=expected_name, description=expected_description, tags=expected_tags, attributes=expected_attributes, profile=self.profile)

        # Assert
        self.assertEqual(expected_name, world.name)
        self.assertEqual(expected_description, world.description)
        self.assertEqual(expected_tags, world.tags)
        self.assertEqual(expected_attributes, world.attributes)

    def test__retrieve__should_return_saved__when_exists(self) -> None:
        # Arrange
        expected = self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)

        # Act
        actual = self.world_use_case.retrieve(expected.id, profile=self.profile)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def action(): self.world_use_case.retrieve(anon_prefixed_id(prefix="world"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve__should_raise_exception__when_invalid_id_provided(self) -> None:
        # Arrange

        # Act
        def action(): self.world_use_case.retrieve(anon_prefixed_id(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__retrieve_all__should_return_all_saved__when_no_filters_provided(self) -> None:
        # Arrange
        world_a = self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)
        world_b = self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)
        expected = {world_a, world_b}

        # Act
        actual = self.world_use_case.retrieve_all(profile=self.profile)

        # Assert
        self.assertSetEqual(expected, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_named_entities")
    def test__retrieve_all__should_delegate_to_filter_named_entities__when_filtering_necessary(
            self, filter_named_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_world()}
        filter_named_entities_mock.return_value = expected_output, {}
        expected_input = {self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)}

        # Act
        actual = self.world_use_case.retrieve_all(profile=self.profile)
        
        # Assert
        filter_named_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__retrieve_all__should_delegate_to_filter_tagged_entities__when_filtering_necessary(
            self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_world()}
        filter_tagged_entities_mock.return_value = expected_output, {}
        expected_input = {self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)}

        # Act
        actual = self.world_use_case.retrieve_all(profile=self.profile)

        # Assert
        filter_tagged_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    def test__retrieve_all__should_raise_exception__when_unsupported_filter_provided(self) -> None:
        # Arrange

        # Act
        def action(): self.world_use_case.retrieve_all(unsupported_filter=anon_anything(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__update__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def action(): self.world_use_case.update(anon_world(), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__update__should_update_provided_attributes__when_attributes_provided(self) -> None:
        # Arrange
        world = self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag(), anon_tag()}
        expected_attributes = anon_attributes()
        modified_world = World(
            id=world.id, name=expected_name, description=expected_description, tags=expected_tags, attributes=expected_attributes)

        # Act
        self.world_use_case.update(modified_world, profile=self.profile)

        # Assert
        actual = self.world_use_case.retrieve(world.id, profile=self.profile)
        self.assertEqual(expected_name, actual.name)
        self.assertEqual(expected_description, actual.description)
        self.assertEqual(expected_tags, actual.tags)
        self.assertEqual(expected_attributes, actual.attributes)

    def test__delete__should_delete__when_world_exists(self) -> None:
        # Arrange
        world = self.world_use_case.create(**anon_create_world_kwargs(), profile=self.profile)

        # Act
        self.world_use_case.delete(world.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, lambda: self.world_use_case.retrieve(world.id, profile=self.profile))

    def test__delete__should_reject_ids_that_do_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.world_use_case.delete(anon_prefixed_id(prefix="world"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__delete__should_reject_invalid_ids(self) -> None:
        # Arrange

        # Act
        def action(): self.world_use_case.delete(anon_prefixed_id(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)
