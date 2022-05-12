from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, MagicMock

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_positional_range, anon_name, anon_description, anon_tag, \
    anon_create_location_kwargs, anon_location, anon_anything, anon_event, anon_attributes
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryEventRepository, InMemoryWorldRepository
from application.access.clients import Profile
from application.use_case.location_use_cases import LocationUseCase
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import EventRepository
from test_helpers.anons import anon_world


class TestLocationUseCase(TestCase):
    event_repository: EventRepository
    location_use_case: LocationUseCase
    profile: Profile
    world_id: PrefixedUUID
    other_world_id: PrefixedUUID

    def setUp(self) -> None:
        world_repository = InMemoryWorldRepository()
        self.event_repository = InMemoryEventRepository()
        self.location_use_case = LocationUseCase(world_repository, InMemoryLocationRepository(), self.event_repository)
        self.profile = Profile(anon_name(), anon_name())
        world_1 = anon_world()
        world_2 = anon_world()
        world_repository.save(world_1)
        world_repository.save(world_2)
        self.world_id = world_1.id
        self.other_world_id = world_2.id

    def test__create__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        location = self.location_use_case.create(self.world_id, name=anon_name(), span=anon_positional_range(), profile=self.profile)

        # Assert
        self.assertTrue(hasattr(location, "id"))

    def test__create__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        location = self.location_use_case.create(self.world_id, id=undesired_id, name=anon_name(), span=anon_positional_range(),
                                                 profile=self.profile)

        # Assert
        self.assertNotEqual(undesired_id, location.id)

    def test__create__should_raise_exception__when_world_does_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.create(anon_prefixed_id(prefix="world"), **anon_create_location_kwargs(), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__create__should_use_provided_args(self) -> None:
        # Arrange
        expected_span = anon_positional_range()
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag()}

        # Act
        location = self.location_use_case.create(self.world_id, span=expected_span, name=expected_name, description=expected_description,
                                                 profile=self.profile, tags=expected_tags)

        # Assert
        self.assertEqual(expected_span, location.span)
        self.assertEqual(expected_name, location.name)
        self.assertEqual(expected_description, location.description)
        self.assertEqual(expected_tags, location.tags)

    def test__retrieve__should_return_saved__when_exists_for_given_world(self) -> None:
        # Arrange
        expected = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())

        # Act
        actual = self.location_use_case.retrieve(self.world_id, expected.id, profile=self.profile)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve__should_raise_exception__when_exists_for_another_world(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.other_world_id, profile=self.profile, **anon_create_location_kwargs())

        # Act
        def action(): self.location_use_case.retrieve(self.world_id, location.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve__should_raise_exception__when_world_does_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.retrieve(
            anon_prefixed_id(prefix="world"), anon_prefixed_id(prefix="location"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve__should_raise_exception__when_location_does_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.retrieve(self.world_id, anon_prefixed_id(prefix="location"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve__should_raise_exception__when_invalid_id_provided(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.retrieve(self.world_id, anon_prefixed_id(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__retrieve_all__should_raise_exception__when_world_does_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.retrieve_all(anon_prefixed_id(prefix="world"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve_all__should_return_all_saved_for_world__when_no_filters_provided(self) -> None:
        # Arrange
        location_a = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())
        location_b = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())
        expected = {location_a, location_b}

        # Act
        actual = self.location_use_case.retrieve_all(self.world_id, profile=self.profile)

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_not_return_any_saved_for_another_world__when_no_filters_provided(self) -> None:
        # Arrange
        self.location_use_case.create(self.other_world_id, profile=self.profile, **anon_create_location_kwargs())
        location_b = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())
        self.location_use_case.create(self.other_world_id, profile=self.profile, **anon_create_location_kwargs())
        expected = {location_b}

        # Act
        actual = self.location_use_case.retrieve_all(self.world_id, profile=self.profile)

        # Assert
        self.assertSetEqual(expected, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_named_entities")
    def test__retrieve_all__should_delegate_to_filter_named_entities__when_filtering_necessary(
            self, filter_named_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_location()}
        filter_named_entities_mock.return_value = expected_output, {}
        expected_input = {self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())}

        # Act
        actual = self.location_use_case.retrieve_all(self.world_id, profile=self.profile)

        # Assert
        filter_named_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__retrieve_all__should_delegate_to_filter_tagged_entities__when_filtering_necessary(
            self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_location()}
        filter_tagged_entities_mock.return_value = expected_output, {}
        expected_input = {self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())}

        # Act
        actual = self.location_use_case.retrieve_all(self.world_id, profile=self.profile)

        # Assert
        filter_tagged_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_spanning_entities")
    def test__retrieve_all__should_delegate_to_filter_spanning_entities__when_filtering_necessary(
            self, filter_spanning_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_location()}
        filter_spanning_entities_mock.return_value = expected_output, {}
        expected_input = {self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())}

        # Act
        actual = self.location_use_case.retrieve_all(self.world_id, profile=self.profile)

        # Assert
        filter_spanning_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    def test__retrieve_all__should_raise_exception__when_unsupported_filter_provided(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.retrieve_all(self.world_id, unsupported_filter=anon_anything(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__update__should_raise_exception__when_world_does_not_exist(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())

        # Act
        def action(): self.location_use_case.update(anon_prefixed_id(prefix="world"), location.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__update__should_raise_exception__when_location_does_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.update(self.world_id, anon_location(), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__update__should_reject_attempts_to_change_span_causing_it_to_no_longer_intersect_linked_events(self) -> None:
        # Arrange
        span = anon_positional_range()
        location_kwargs = anon_create_location_kwargs(span=span)
        location = self.location_use_case.create(self.world_id, profile=self.profile, **location_kwargs)
        self.event_repository.save(anon_event(affected_locations={location.id}, span=span))
        modified_kwargs = deepcopy(location_kwargs)
        modified_kwargs["id"] = location.id
        modified_kwargs["span"] = anon_positional_range()
        modified_location = Location(**modified_kwargs)

        # Act
        # noinspection PyArgumentList
        def action(): self.location_use_case.update(self.world_id, modified_location, profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__update__should_update_provided_attributes__when_attributes_provided(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())
        expected_name = anon_name()
        expected_description = anon_description()
        expected_span = anon_positional_range()
        expected_tags = {anon_tag(), anon_tag()}
        expected_attributes = anon_attributes()
        modified_location = Location(
            id=location.id, name=expected_name, description=expected_description, span=expected_span, tags=expected_tags,
            attributes=expected_attributes)

        # Act
        self.location_use_case.update(self.world_id, modified_location, profile=self.profile)

        # Assert
        actual = self.location_use_case.retrieve(self.world_id, location.id, profile=self.profile)
        self.assertEqual(expected_name, actual.name)
        self.assertEqual(expected_description, actual.description)
        self.assertEqual(expected_span, actual.span)
        self.assertEqual(expected_tags, actual.tags)
        self.assertEqual(expected_attributes, actual.attributes)

    def test__delete__should_delete__when_location_exists_for_world(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())

        # Act
        self.location_use_case.delete(self.world_id, location.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, lambda: self.location_use_case.retrieve(self.world_id, location.id, profile=self.profile))

    def test__delete__should_reject_ids_that_exist_for_another_world(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.other_world_id, profile=self.profile, **anon_create_location_kwargs())

        # Act
        def action(): self.location_use_case.delete(self.world_id, location.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__delete__should_reject_ids_that_do_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.delete(self.world_id, anon_prefixed_id(prefix="location"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__delete__should_raise_exception__when_world_does_not_exist(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.delete(
            anon_prefixed_id(prefix="world"), anon_prefixed_id(prefix="location"), profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__delete__should_reject_invalid_ids(self) -> None:
        # Arrange

        # Act
        def action(): self.location_use_case.delete(self.world_id, anon_prefixed_id(), profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)

    def test__delete__should_reject_attempts_to_delete_locations_that_are_linked_to_an_event(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.world_id, profile=self.profile, **anon_create_location_kwargs())
        self.event_repository.save(anon_event(affected_locations={location.id}))

        # Act
        def action(): self.location_use_case.delete(self.world_id, location.id, profile=self.profile)

        # Assert
        self.assertRaises(ValueError, action)
