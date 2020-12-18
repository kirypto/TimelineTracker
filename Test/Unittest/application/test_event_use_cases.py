from unittest import TestCase
from unittest.mock import patch, MagicMock

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_positional_range, anon_name, anon_description, anon_tag, \
    anon_create_event_kwargs, anon_event, anon_anything, anon_location, anon_traveler
from adapter.persistence.in_memory_repositories import InMemoryEventRepository, InMemoryLocationRepository, InMemoryTravelerRepository
from application.event_use_cases import EventUseCase
from domain.persistence.repositories import TravelerRepository, LocationRepository
from domain.positions import PositionalMove, MovementType, Position


class TestEventUsecase(TestCase):
    event_use_case: EventUseCase
    location_repository: LocationRepository
    traveler_repository: TravelerRepository

    def setUp(self) -> None:
        self.location_repository = InMemoryLocationRepository()
        self.traveler_repository = InMemoryTravelerRepository()
        self.event_use_case = EventUseCase(self.location_repository, self.traveler_repository, InMemoryEventRepository())

    def test__create__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        event = self.event_use_case.create(name=anon_name(), span=anon_positional_range())

        # Assert
        self.assertTrue(hasattr(event, "id"))

    def test__create__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        event = self.event_use_case.create(id=undesired_id, name=anon_name(), span=anon_positional_range())

        # Assert
        self.assertNotEqual(undesired_id, event.id)

    def test__create__should_use_provided_args__when_affected_travelers_and_locations_not_provided(self) -> None:
        # Arrange
        expected_span = anon_positional_range()
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag()}

        # Act
        event = self.event_use_case.create(span=expected_span, name=expected_name, description=expected_description,
                                           tags=expected_tags, affected_locations=set(), affected_travelers=set())

        # Assert
        self.assertEqual(expected_span, event.span)
        self.assertEqual(expected_name, event.name)
        self.assertEqual(expected_description, event.description)
        self.assertSetEqual(expected_tags, event.tags)
        self.assertSetEqual(set(), event.affected_locations)
        self.assertSetEqual(set(), event.affected_travelers)

    def test__create__should_use_provided_args__when_affected_travelers_and_locations_intersect_events(self) -> None:
        # Arrange
        span = anon_positional_range()
        location = anon_location(span=span)
        journey = [PositionalMove(
            position=Position(latitude=span.latitude.low, longitude=span.longitude.low, altitude=span.altitude.low, continuum=span.continuum.low,
                              reality=span.reality.low), movement_type=MovementType.IMMEDIATE)]
        traveler = anon_traveler(journey=journey)
        self.location_repository.save(location)
        self.traveler_repository.save(traveler)

        # Act
        event = self.event_use_case.create(span=span, name=anon_name(), description=anon_description(), tags={anon_tag()},
                                           affected_travelers={traveler.id}, affected_locations={location.id})

        # Assert
        self.assertSetEqual({location.id}, event.affected_locations)
        self.assertSetEqual({traveler.id}, event.affected_travelers)

    def test__create__should_reject_affected_locations_that_do_not_intersect_event(self) -> None:
        # Arrange
        location = anon_location()
        self.location_repository.save(location)

        # Act
        def Action(): self.event_use_case.create(span=anon_positional_range(), name=anon_name(), description=anon_description(), tags={anon_tag()},
                                                 affected_locations={location.id})

        # Assert
        self.assertRaises(ValueError, Action)

    def test__create__should_reject_affected_travelers_that_do_not_intersect_event(self) -> None:
        # Arrange
        traveler = anon_traveler()
        self.traveler_repository.save(traveler)

        # Act
        def Action(): self.event_use_case.create(span=anon_positional_range(), name=anon_name(), description=anon_description(), tags={anon_tag()},
                                                 affected_travelers={traveler.id})

        # Assert
        self.assertRaises(ValueError, Action)

    def test__retrieve__should_return_saved__when_exists(self) -> None:
        # Arrange
        expected = self.event_use_case.create(**anon_create_event_kwargs())

        # Act
        actual = self.event_use_case.retrieve(expected.id)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def Action(): self.event_use_case.retrieve(anon_prefixed_id(prefix="event"))

        # Assert
        self.assertRaises(NameError, Action)

    def test__retrieve__should_raise_exception__when_invalid_id_provided(self) -> None:
        # Arrange

        # Act
        def Action(): self.event_use_case.retrieve(anon_prefixed_id())

        # Assert
        self.assertRaises(ValueError, Action)

    def test__retrieve_all__should_return_all_saved__when_no_filters_provided(self) -> None:
        # Arrange
        event_a = self.event_use_case.create(**anon_create_event_kwargs())
        event_b = self.event_use_case.create(**anon_create_event_kwargs())
        expected = {event_a, event_b}

        # Act
        actual = self.event_use_case.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)

    @patch("application.filtering_use_cases.FilteringUseCase.filter_named_entities")
    def test__retrieve_all__should_delegate_to_filter_named_entities__when_filtering_necessary(self, filter_named_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_event()}
        filter_named_entities_mock.return_value = expected_output, {}
        expected_input = {self.event_use_case.create(**anon_create_event_kwargs())}

        # Act
        actual = self.event_use_case.retrieve_all()

        # Assert
        filter_named_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    @patch("application.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__retrieve_all__should_delegate_to_filter_tagged_entities__when_filtering_necessary(self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_event()}
        filter_tagged_entities_mock.return_value = expected_output, {}
        expected_input = {self.event_use_case.create(**anon_create_event_kwargs())}

        # Act
        actual = self.event_use_case.retrieve_all()

        # Assert
        filter_tagged_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    @patch("application.filtering_use_cases.FilteringUseCase.filter_spanning_entities")
    def test__retrieve_all__should_delegate_to_filter_spanning_entities__when_filtering_necessary(self,
                                                                                                  filter_spanning_entities_mock: MagicMock) -> None:
        # Arrange
        expected_output = {anon_event()}
        filter_spanning_entities_mock.return_value = expected_output, {}
        expected_input = {self.event_use_case.create(**anon_create_event_kwargs())}

        # Act
        actual = self.event_use_case.retrieve_all()

        # Assert
        filter_spanning_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    def test__retrieve_all__should_raise_exception__when_unsupported_filter_provided(self) -> None:
        # Arrange

        # Act
        def Action(): self.event_use_case.retrieve_all(unsupported_filter=anon_anything())

        # Assert
        self.assertRaises(ValueError, Action)

    def test__update__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def Action(): self.event_use_case.update(anon_prefixed_id(prefix="event"), name=anon_name())

        # Assert
        self.assertRaises(NameError, Action)

    def test__update__should_reject_attempts_to_change_id(self) -> None:
        # Arrange
        event = self.event_use_case.create(**anon_create_event_kwargs())

        # Act
        # noinspection PyArgumentList
        def Action(): self.event_use_case.update(event.id, id=anon_prefixed_id(prefix="event"))

        # Assert
        self.assertRaises(ValueError, Action)

    def test__update__should_reject_affected_locations_that_do_not_intersect_event(self) -> None:
        # Arrange
        event = self.event_use_case.create(**anon_create_event_kwargs())
        location = anon_location()
        self.location_repository.save(location)

        # Act
        def Action(): self.event_use_case.update(event.id, affected_locations={location.id})

        # Assert
        self.assertRaises(ValueError, Action)

    def test__update__should_reject_affected_travelers_that_do_not_intersect_event(self) -> None:
        # Arrange
        event = self.event_use_case.create(**anon_create_event_kwargs())
        traveler = anon_traveler()
        self.traveler_repository.save(traveler)

        # Act
        def Action(): self.event_use_case.update(event.id, affected_travelers={traveler.id})

        # Assert
        self.assertRaises(ValueError, Action)

    def test__update__should_update_provided_attributes__when_attributes_provided(self) -> None:
        # Arrange
        event = self.event_use_case.create(**anon_create_event_kwargs())
        expected_name = anon_name()
        expected_description = anon_description()
        expected_span = anon_positional_range()
        expected_tags = {anon_tag(), anon_tag()}

        # Act
        actual_updated_name = self.event_use_case.update(event.id, name=expected_name)
        actual_updated_description = self.event_use_case.update(event.id, description=expected_description)
        actual_updated_span = self.event_use_case.update(event.id, span=expected_span)
        actual_updated_tags = self.event_use_case.update(event.id, tags=expected_tags)

        # Assert
        self.assertEqual(expected_name, actual_updated_name.name)
        self.assertEqual(expected_description, actual_updated_description.description)
        self.assertEqual(expected_span, actual_updated_span.span)
        self.assertEqual(expected_tags, actual_updated_tags.tags)

    def test__delete__should_delete__when_event_exists(self) -> None:
        # Arrange
        event = self.event_use_case.create(**anon_create_event_kwargs())

        # Act
        self.event_use_case.delete(event.id)

        # Assert
        self.assertRaises(NameError, lambda: self.event_use_case.retrieve(event.id))

    def test__delete__should_raise_exception__when_not_exits(self) -> None:
        # Arrange

        # Act
        def Action(): self.event_use_case.delete(anon_prefixed_id(prefix="event"))

        # Assert
        self.assertRaises(NameError, Action)

    def test__delete__should_raise_exception__when_invalid_id_provided(self) -> None:
        # Arrange

        # Act
        def Action(): self.event_use_case.delete(anon_prefixed_id())

        # Assert
        self.assertRaises(ValueError, Action)
