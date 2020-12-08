from unittest import TestCase
from unittest.mock import patch, MagicMock

from Test.Unittest.test_helpers.anons import anon_journey, anon_prefixed_id, anon_name, anon_description, anon_tag, \
    anon_create_traveler_kwargs, anon_traveler, anon_anything
from adapter.persistence.in_memory_repositories import InMemoryTravelerRepository
from application.traveler_use_cases import TravelerUseCase


class TestTravelerUsecase(TestCase):
    traveler_use_case: TravelerUseCase

    def setUp(self) -> None:
        self.traveler_use_case = TravelerUseCase(InMemoryTravelerRepository())

    def test__create__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        traveler = self.traveler_use_case.create(journey=anon_journey())

        # Assert
        self.assertTrue(hasattr(traveler, "id"))

    def test__create__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        traveler = self.traveler_use_case.create(id=undesired_id, journey=anon_journey())

        # Assert
        self.assertNotEqual(undesired_id, traveler.id)

    def test__create__should_use_provided_args(self) -> None:
        # Arrange
        expected_journey = anon_journey()
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag()}

        # Act
        traveler = self.traveler_use_case.create(journey=expected_journey, name=expected_name, description=expected_description,
                                                 tags=expected_tags)

        # Assert
        self.assertEqual(expected_journey, traveler.journey)
        self.assertEqual(expected_name, traveler.name)
        self.assertEqual(expected_description, traveler.description)
        self.assertEqual(expected_tags, traveler.tags)

    def test__retrieve__should_return_saved__when_exists(self) -> None:
        # Arrange
        expected = self.traveler_use_case.create(**anon_create_traveler_kwargs())

        # Act
        actual = self.traveler_use_case.retrieve(expected.id)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def Action(): self.traveler_use_case.retrieve(anon_prefixed_id(prefix="traveler"))

        # Assert
        self.assertRaises(NameError, Action)

    def test__retrieve__should_raise_exception__when_invalid_id_provided(self) -> None:
        # Arrange

        # Act
        def Action(): self.traveler_use_case.retrieve(anon_prefixed_id())

        # Assert
        self.assertRaises(ValueError, Action)

    def test__retrieve_all__should_return_all_saved__when_no_filters_provided(self) -> None:
        # Arrange
        traveler_a = self.traveler_use_case.create(**anon_create_traveler_kwargs())
        traveler_b = self.traveler_use_case.create(**anon_create_traveler_kwargs())
        expected = {traveler_a, traveler_b}

        # Act
        actual = self.traveler_use_case.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)

    @patch("application.filtering_use_cases.FilteringUseCase.filter_named_entities")
    def test__retrieve_all__should_delegate_to_filter_named_entities__when_filtering_necessary(self, filter_named_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_traveler()}
        filter_named_entities_mock.return_value = expected_output, {}
        expected_input = {self.traveler_use_case.create(**anon_create_traveler_kwargs())}

        # Act
        actual = self.traveler_use_case.retrieve_all()

        # Assert
        self.assertEqual(expected_output, actual)
        filter_named_entities_mock.assert_called_once_with(expected_input)

    @patch("application.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__retrieve_all__should_delegate_to_filter_tagged_entities__when_filtering_necessary(self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_traveler()}
        filter_tagged_entities_mock.return_value = expected_output, {}
        expected_input = {self.traveler_use_case.create(**anon_create_traveler_kwargs())}

        # Act
        actual = self.traveler_use_case.retrieve_all()

        # Assert
        self.assertEqual(expected_output, actual)
        filter_tagged_entities_mock.assert_called_once_with(expected_input)

    @patch("application.filtering_use_cases.FilteringUseCase.filter_journeying_entities")
    def test__retrieve_all__should_delegate_to_filter_journeying_entities__when_filtering_necessary(self, filter_journeying_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_traveler()}
        filter_journeying_entities_mock.return_value = expected_output, {}
        expected_input = {self.traveler_use_case.create(**anon_create_traveler_kwargs())}

        # Act
        actual = self.traveler_use_case.retrieve_all()

        # Assert
        filter_journeying_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    def test__retrieve_all__should_raise_exception__when_unsupported_filter_provided(self) -> None:
        # Arrange

        # Act
        def Action(): self.traveler_use_case.retrieve_all(unsupported_filter=anon_anything())

        # Assert
        self.assertRaises(ValueError, Action)

    def test__update__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def Action(): self.traveler_use_case.update(anon_prefixed_id(prefix="traveler"), name=anon_name())

        # Assert
        self.assertRaises(NameError, Action)

    def test__update__should_reject_attempts_to_change_id(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(**anon_create_traveler_kwargs())

        # Act
        # noinspection PyArgumentList
        def Action(): self.traveler_use_case.update(traveler.id, id=anon_prefixed_id(prefix="traveler"))

        # Assert
        self.assertRaises(TypeError, Action)

    def test__update__should_update_provided_attributes__when_attributes_provided(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(**anon_create_traveler_kwargs())
        expected_name = anon_name()
        expected_description = anon_description()
        expected_journey = anon_journey()
        expected_tags = {anon_tag(), anon_tag()}

        # Act
        actual_updated_name = self.traveler_use_case.update(traveler.id, name=expected_name)
        actual_updated_description = self.traveler_use_case.update(traveler.id, description=expected_description)
        actual_updated_journey = self.traveler_use_case.update(traveler.id, journey=expected_journey)
        actual_updated_tags = self.traveler_use_case.update(traveler.id, tags=expected_tags)

        # Assert
        self.assertEqual(expected_name, actual_updated_name.name)
        self.assertEqual(expected_description, actual_updated_description.description)
        self.assertEqual(expected_journey, actual_updated_journey.journey)
        self.assertEqual(expected_tags, actual_updated_tags.tags)

    def test__delete__should_delete__when_traveler_exists(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(**anon_create_traveler_kwargs())

        # Act
        self.traveler_use_case.delete(traveler.id)

        # Assert
        self.assertRaises(NameError, lambda: self.traveler_use_case.retrieve(traveler.id))

    def test__delete__should_raise_exception__when_not_exits(self) -> None:
        # Arrange

        # Act
        def Action(): self.traveler_use_case.delete(anon_prefixed_id(prefix="traveler"))

        # Assert
        self.assertRaises(NameError, Action)

    def test__delete__should_raise_exception__when_invalid_id_given(self) -> None:
        # Arrange

        # Act
        def Action(): self.traveler_use_case.delete(anon_prefixed_id())

        # Assert
        self.assertRaises(ValueError, Action)
