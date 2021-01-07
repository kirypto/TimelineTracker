from math import inf
from random import shuffle
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_event, anon_positional_range, anon_location
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository, InMemoryEventRepository
from application.timeline_use_cases import TimelineUseCase
from domain.collections import Range
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository


class TestTimelineUseCase(TestCase):
    location_repository: LocationRepository
    traveler_repository: TravelerRepository
    event_repository: EventRepository
    timeline_use_case: TimelineUseCase

    def setUp(self) -> None:
        self.location_repository = InMemoryLocationRepository()
        self.traveler_repository = InMemoryTravelerRepository()
        self.event_repository = InMemoryEventRepository()
        self.timeline_use_case = TimelineUseCase(self.location_repository, self.event_repository)

    def test__construct_location_timeline__should_reject_nonexistent_location(self) -> None:
        # Arrange
        location_id = anon_prefixed_id(prefix="location")

        # Act
        def action(): self.timeline_use_case.construct_location_timeline(location_id)
        
        # Assert
        self.assertRaises(NameError, action)

    def test__construct_location_timeline__should_return_list_of_linked_events_ordered_by_continuum_low_and_then_high(self) -> None:
        # Arrange
        location_id = anon_prefixed_id(prefix="location")
        continuum_1 = Range(-inf, -56.)
        continuum_2 = Range(-58., -20.)
        continuum_3 = Range(-19., 20.)
        continuum_4 = Range(-18., 20.)
        continuum_5 = Range(22., 42.)
        continuum_6 = Range(22., 43.)
        continuum_7 = Range(25., inf)
        event_1 = anon_event(span=anon_positional_range(continuum=continuum_1), affected_locations={location_id}, affected_travelers=set())
        event_2 = anon_event(span=anon_positional_range(continuum=continuum_2), affected_locations={location_id}, affected_travelers=set())
        event_3 = anon_event(span=anon_positional_range(continuum=continuum_3), affected_locations={location_id}, affected_travelers=set())
        event_4 = anon_event(span=anon_positional_range(continuum=continuum_4), affected_locations={location_id}, affected_travelers=set())
        event_5 = anon_event(span=anon_positional_range(continuum=continuum_5), affected_locations={location_id}, affected_travelers=set())
        event_6 = anon_event(span=anon_positional_range(continuum=continuum_6), affected_locations={location_id}, affected_travelers=set())
        event_7 = anon_event(span=anon_positional_range(continuum=continuum_7), affected_locations={location_id}, affected_travelers=set())
        events = [event_1, event_2, event_3, event_4, event_5, event_6, event_7]
        expected_timeline = [event.id for event in events]
        shuffle(events)
        self.location_repository.save(anon_location(id=location_id))
        for event in events:
            self.event_repository.save(event)

        # Act
        actual = self.timeline_use_case.construct_location_timeline(location_id)

        # Assert
        self.assertListEqual(expected_timeline, actual)
