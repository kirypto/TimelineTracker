from math import inf
from random import shuffle
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_event, anon_positional_range, anon_location, anon_traveler
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository, InMemoryEventRepository
from application.timeline_use_cases import TimelineUseCase
from domain.collections import Range
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository
from domain.positions import Position, PositionalMove, MovementType, PositionalRange


class TestTimelineUseCase(TestCase):
    location_repository: LocationRepository
    traveler_repository: TravelerRepository
    event_repository: EventRepository
    timeline_use_case: TimelineUseCase

    def setUp(self) -> None:
        self.location_repository = InMemoryLocationRepository()
        self.traveler_repository = InMemoryTravelerRepository()
        self.event_repository = InMemoryEventRepository()
        self.timeline_use_case = TimelineUseCase(self.location_repository, self.traveler_repository, self.event_repository)
        self.maxDiff = None

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
        event_1 = anon_event(span=anon_positional_range(continuum=continuum_1), affected_locations={location_id})
        event_2 = anon_event(span=anon_positional_range(continuum=continuum_2), affected_locations={location_id})
        event_3 = anon_event(span=anon_positional_range(continuum=continuum_3), affected_locations={location_id})
        event_4 = anon_event(span=anon_positional_range(continuum=continuum_4), affected_locations={location_id})
        event_5 = anon_event(span=anon_positional_range(continuum=continuum_5), affected_locations={location_id})
        event_6 = anon_event(span=anon_positional_range(continuum=continuum_6), affected_locations={location_id})
        event_7 = anon_event(span=anon_positional_range(continuum=continuum_7), affected_locations={location_id})
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

    def test__construct_traveler_timeline__should_reject_nonexistent_traveler(self) -> None:
        # Arrange
        traveler_id = anon_prefixed_id(prefix="traveler")

        # Act
        def action(): self.timeline_use_case.construct_traveler_timeline(traveler_id)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_traveler_timeline__should_return_same_event_multiple_times_when_travelers_journey_intersects_it_multiple_times(self) -> None:
        # Arrange
        initially_on_ground = Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0)
        jumping_upward = Position(latitude=1, longitude=1, altitude=5, continuum=2, reality=0)
        jump_peak = Position(latitude=1, longitude=1, altitude=10, continuum=3, reality=0)
        falling_downward = Position(latitude=1, longitude=1, altitude=5, continuum=4, reality=0)
        back_on_ground = Position(latitude=1, longitude=1, altitude=0, continuum=5, reality=0)

        near_ground_span = PositionalRange(latitude=Range(-2, 2), longitude=Range(-2, 2), altitude=Range(-2, 2), continuum=Range(0, 5),
                                           reality=Range(0, 0))
        in_air_span = PositionalRange(latitude=Range(-2, 2), longitude=Range(-2, 2), altitude=Range(8, 12), continuum=Range(0, 5),
                                      reality=Range(0, 0))

        traveler = anon_traveler(journey=[
            PositionalMove(position=initially_on_ground, movement_type=MovementType.IMMEDIATE),
            PositionalMove(position=jumping_upward, movement_type=MovementType.INTERPOLATED),
            PositionalMove(position=jump_peak, movement_type=MovementType.INTERPOLATED),
            PositionalMove(position=falling_downward, movement_type=MovementType.INTERPOLATED),
            PositionalMove(position=back_on_ground, movement_type=MovementType.INTERPOLATED),
        ])
        on_ground_event = anon_event(span=near_ground_span, affected_travelers={traveler.id})
        in_air_event = anon_event(span=in_air_span, affected_travelers={traveler.id})

        self.traveler_repository.save(traveler)
        self.event_repository.save(on_ground_event)
        self.event_repository.save(in_air_event)

        expected_timeline = [
            initially_on_ground,
            on_ground_event.id,
            jumping_upward,
            in_air_event.id,
            jump_peak,
            falling_downward,
            on_ground_event.id,
            back_on_ground,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(traveler.id)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    def test__construct_traveler_timeline__should_put_affecting_events_after_the_position__when_movement_type_is_immediate(self) -> None:
        # Arrange
        outside_affected_area = Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0)
        inside_affected_area = Position(latitude=5, longitude=1, altitude=0, continuum=2, reality=0)

        affected_area = PositionalRange(latitude=Range(4, 6), longitude=Range(1, 1), altitude=Range(0, 0), continuum=Range(0, 3), reality=Range(0, 0))

        traveler = anon_traveler(journey=[
            PositionalMove(position=outside_affected_area, movement_type=MovementType.IMMEDIATE),
            PositionalMove(position=inside_affected_area, movement_type=MovementType.IMMEDIATE),
        ])
        event = anon_event(span=affected_area, affected_travelers={traveler.id})

        self.traveler_repository.save(traveler)
        self.event_repository.save(event)

        expected_timeline = [
            outside_affected_area,
            inside_affected_area,
            event.id,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(traveler.id)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    def test__construct_traveler_timeline__should_put_affecting_events_before_the_position__when_movement_type_is_interpolated(self) -> None:
        # Arrange
        outside_affected_area = Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0)
        inside_affected_area = Position(latitude=5, longitude=1, altitude=0, continuum=2, reality=0)

        affected_area = PositionalRange(latitude=Range(4, 6), longitude=Range(1, 1), altitude=Range(0, 0), continuum=Range(0, 3), reality=Range(0, 0))

        traveler = anon_traveler(journey=[
            PositionalMove(position=outside_affected_area, movement_type=MovementType.IMMEDIATE),
            PositionalMove(position=inside_affected_area, movement_type=MovementType.INTERPOLATED),
        ])
        event = anon_event(span=affected_area, affected_travelers={traveler.id})

        self.traveler_repository.save(traveler)
        self.event_repository.save(event)

        expected_timeline = [
            outside_affected_area,
            event.id,
            inside_affected_area,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(traveler.id)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    def test__construct_traveler_timeline__should_not_report_same_event_multiple_times__when_traveler_does_not_leave_events_span(self) -> None:
        # Arrange
        pos_1_outside_affected_area = Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0)
        pos_2_inside_affected_area_a = Position(latitude=5, longitude=1, altitude=0, continuum=2, reality=0)
        pos_3_inside_affected_area_b = Position(latitude=6, longitude=1, altitude=0, continuum=3, reality=0)
        pos_4_inside_affected_area_a = Position(latitude=5, longitude=1, altitude=0, continuum=4, reality=0)
        pos_5_outside_affected_area = Position(latitude=1, longitude=1, altitude=0, continuum=5, reality=0)
        pos_6_inside_affected_area_b = Position(latitude=6, longitude=1, altitude=0, continuum=6, reality=0)

        affected_area = PositionalRange(latitude=Range(4, 6), longitude=Range(1, 1), altitude=Range(0, 0), continuum=Range(0, 6), reality=Range(0, 0))

        traveler = anon_traveler(journey=[
            PositionalMove(position=pos_1_outside_affected_area, movement_type=MovementType.IMMEDIATE),
            PositionalMove(position=pos_2_inside_affected_area_a, movement_type=MovementType.INTERPOLATED),
            PositionalMove(position=pos_3_inside_affected_area_b, movement_type=MovementType.INTERPOLATED),
            PositionalMove(position=pos_4_inside_affected_area_a, movement_type=MovementType.IMMEDIATE),
            PositionalMove(position=pos_5_outside_affected_area, movement_type=MovementType.INTERPOLATED),
            PositionalMove(position=pos_6_inside_affected_area_b, movement_type=MovementType.INTERPOLATED),
        ])
        event = anon_event(span=affected_area, affected_travelers={traveler.id})

        self.traveler_repository.save(traveler)
        self.event_repository.save(event)

        expected_timeline = [
            pos_1_outside_affected_area,
            event.id,
            pos_2_inside_affected_area_a,
            pos_3_inside_affected_area_b,
            pos_4_inside_affected_area_a,
            pos_5_outside_affected_area,
            event.id,
            pos_6_inside_affected_area_b,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(traveler.id)

        # Assert
        self.assertListEqual(expected_timeline, actual)
