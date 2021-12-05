from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, MagicMock

from Test.Unittest.test_helpers.anons import anon_journey, anon_prefixed_id, anon_name, anon_description, anon_tag, \
    anon_create_traveler_kwargs, anon_traveler, anon_anything, anon_positional_range, anon_event, anon_metadata
from adapter.persistence.in_memory_repositories import InMemoryTravelerRepository, InMemoryEventRepository
from application.access.clients import Profile
from application.use_case.traveler_use_cases import TravelerUseCase
from domain.persistence.repositories import EventRepository
from domain.positions import PositionalMove, MovementType, Position
from domain.travelers import Traveler


class TestTravelerUseCase(TestCase):
    event_repository: EventRepository
    traveler_use_case: TravelerUseCase
    profile: Profile

    def setUp(self) -> None:
        self.event_repository = InMemoryEventRepository()
        self.traveler_use_case = TravelerUseCase(InMemoryTravelerRepository(), self.event_repository)
        self.profile = Profile(anon_name(), anon_name())

    def test__create__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        traveler = self.traveler_use_case.create(name=anon_name(), journey=anon_journey(), profile=self.profile)

        # Assert
        self.assertTrue(hasattr(traveler, "id"))

    def test__create__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        traveler = self.traveler_use_case.create(id=undesired_id, name=anon_name(), journey=anon_journey(), profile=self.profile)

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
                                                 tags=expected_tags, profile=self.profile)

        # Assert
        self.assertEqual(expected_journey, traveler.journey)
        self.assertEqual(expected_name, traveler.name)
        self.assertEqual(expected_description, traveler.description)
        self.assertEqual(expected_tags, traveler.tags)

    def test__retrieve__should_return_saved__when_exists(self) -> None:
        # Arrange
        expected = self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)

        # Act
        actual = self.traveler_use_case.retrieve(expected.id, profile=self.profile)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def action(): self.traveler_use_case.retrieve(anon_prefixed_id(prefix="traveler"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve__should_raise_exception__when_invalid_id_provided(self) -> None:
        # Arrange

        # Act
        def action(): self.traveler_use_case.retrieve(anon_prefixed_id(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__retrieve_all__should_return_all_saved__when_no_filters_provided(self) -> None:
        # Arrange
        traveler_a = self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)
        traveler_b = self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)
        expected = {traveler_a, traveler_b}

        # Act
        actual = self.traveler_use_case.retrieve_all(profile=self.profile)

        # Assert
        self.assertSetEqual(expected, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_named_entities")
    def test__retrieve_all__should_delegate_to_filter_named_entities__when_filtering_necessary(
            self, filter_named_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_traveler()}
        filter_named_entities_mock.return_value = expected_output, {}
        expected_input = {self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)}

        # Act
        actual = self.traveler_use_case.retrieve_all(profile=self.profile)

        # Assert
        self.assertEqual(expected_output, actual)
        filter_named_entities_mock.assert_called_once_with(expected_input)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__retrieve_all__should_delegate_to_filter_tagged_entities__when_filtering_necessary(
            self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_traveler()}
        filter_tagged_entities_mock.return_value = expected_output, {}
        expected_input = {self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)}

        # Act
        actual = self.traveler_use_case.retrieve_all(profile=self.profile)

        # Assert
        self.assertEqual(expected_output, actual)
        filter_tagged_entities_mock.assert_called_once_with(expected_input)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_journeying_entities")
    def test__retrieve_all__should_delegate_to_filter_journeying_entities__when_filtering_necessary(
            self, filter_journeying_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_traveler()}
        filter_journeying_entities_mock.return_value = expected_output, {}
        expected_input = {self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)}

        # Act
        actual = self.traveler_use_case.retrieve_all(profile=self.profile)

        # Assert
        filter_journeying_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    def test__retrieve_all__should_raise_exception__when_unsupported_filter_provided(self) -> None:
        # Arrange

        # Act
        def action(): self.traveler_use_case.retrieve_all(unsupported_filter=anon_anything(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__update__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def action(): self.traveler_use_case.update(anon_traveler(), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__update__should_reject_attempts_to_change_journey_causing_it_to_no_longer_intersect_linked_events(self) -> None:
        # Arrange
        span = anon_positional_range()
        journey = [PositionalMove(
            position=Position(latitude=span.latitude.low, longitude=span.longitude.low, altitude=span.altitude.low,
                              continuum=span.continuum.low, reality=next(iter(span.reality))),
            movement_type=MovementType.IMMEDIATE)]
        traveler_kwargs = anon_create_traveler_kwargs(journey=journey)
        traveler = self.traveler_use_case.create(**traveler_kwargs, profile=self.profile)
        self.event_repository.save(anon_event(affected_travelers={traveler.id}, span=span))
        modified_kwargs = deepcopy(traveler_kwargs)
        modified_kwargs["id"] = traveler.id
        modified_kwargs["journey"] = anon_journey()
        modified_traveler = Traveler(**modified_kwargs)

        # Act
        # noinspection PyArgumentList
        def action(): self.traveler_use_case.update(modified_traveler, profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__update__should_update_provided_attributes__when_attributes_provided(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)
        expected_name = anon_name()
        expected_description = anon_description()
        expected_journey = anon_journey()
        expected_tags = {anon_tag(), anon_tag()}
        expected_metadata = anon_metadata()
        modified_traveler = Traveler(
            id=traveler.id, name=expected_name, description=expected_description, journey=expected_journey,
            tags=expected_tags, metadata=expected_metadata)

        # Act
        self.traveler_use_case.update(modified_traveler, profile=self.profile)

        # Assert
        actual = self.traveler_use_case.retrieve(traveler.id, profile=self.profile)
        self.assertEqual(expected_name, actual.name)
        self.assertEqual(expected_description, actual.description)
        self.assertEqual(expected_journey, actual.journey)
        self.assertEqual(expected_tags, actual.tags)
        self.assertEqual(expected_metadata, actual.metadata)

    def test__delete__should_delete__when_traveler_exists(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)

        # Act
        self.traveler_use_case.delete(traveler.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, lambda: self.traveler_use_case.retrieve(traveler.id, profile=self.profile))

    def test__delete__should_raise_exception__when_not_exits(self) -> None:
        # Arrange

        # Act
        def action(): self.traveler_use_case.delete(anon_prefixed_id(prefix="traveler"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__delete__should_raise_exception__when_invalid_id_given(self) -> None:
        # Arrange

        # Act
        def action(): self.traveler_use_case.delete(anon_prefixed_id(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__delete__should_reject_attempts_to_delete_travelers_that_are_linked_to_an_event(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(**anon_create_traveler_kwargs(), profile=self.profile)
        self.event_repository.save(anon_event(affected_travelers={traveler.id}))

        # Act
        def action(): self.traveler_use_case.delete(traveler.id, profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)
