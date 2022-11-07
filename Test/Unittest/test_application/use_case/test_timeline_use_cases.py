from sys import float_info
from unittest import TestCase
from unittest.mock import patch, MagicMock

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_positional_range, anon_name, \
    anon_world, anon_create_traveler_kwargs
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository, InMemoryEventRepository, \
    InMemoryWorldRepository
from application.access.clients import Profile
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from domain.collections import Range
from domain.ids import PrefixedUUID
from domain.positions import Position, PositionalMove, MovementType, PositionalRange
from test_helpers.anons import anon_create_location_kwargs, anon_create_event_kwargs


FLOAT_MAX_VALUE = float_info.max
FLOAT_MIN_VALUE = -1 * FLOAT_MAX_VALUE


class TestTimelineUseCase(TestCase):
    location_use_case: LocationUseCase
    traveler_use_case: TravelerUseCase
    event_use_case: EventUseCase
    timeline_use_case: TimelineUseCase
    profile: Profile
    world_id: PrefixedUUID
    other_world_id: PrefixedUUID

    def setUp(self) -> None:
        world_repository = InMemoryWorldRepository()
        location_repository = InMemoryLocationRepository()
        traveler_repository = InMemoryTravelerRepository()
        event_repository = InMemoryEventRepository()
        self.location_use_case = LocationUseCase(world_repository, location_repository, event_repository)
        self.traveler_use_case = TravelerUseCase(world_repository, traveler_repository, event_repository)
        self.event_use_case = EventUseCase(world_repository, location_repository, traveler_repository, event_repository)
        self.timeline_use_case = TimelineUseCase(world_repository, location_repository, traveler_repository, event_repository)
        self.maxDiff = None
        self.profile = Profile(anon_name(), anon_name())
        world_1 = anon_world()
        world_2 = anon_world()
        world_repository.save(world_1)
        world_repository.save(world_2)
        self.world_id = world_1.id
        self.other_world_id = world_2.id

    def test__construct_location_timeline__should_reject_nonexistent_world(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.world_id, **anon_create_location_kwargs(), profile=self.profile)
        non_existent_world_id = anon_prefixed_id(prefix="world")

        # Act
        def action(): self.timeline_use_case.construct_location_timeline(non_existent_world_id, location.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_location_timeline__should_reject_nonexistent_location(self) -> None:
        # Arrange
        location_id = anon_prefixed_id(prefix="location")

        # Act
        def action(): self.timeline_use_case.construct_location_timeline(self.world_id, location_id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_location_timeline__should_reject_existent_location_associated_with_another_world(self) -> None:
        # Arrange
        location = self.location_use_case.create(self.world_id, **anon_create_location_kwargs(), profile=self.profile)

        # Act
        def action(): self.timeline_use_case.construct_location_timeline(self.other_world_id, location.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_location_timeline__should_return_list_of_linked_events_ordered_by_continuum_low_and_then_high(self) -> None:
        # Arrange
        large_range = Range(FLOAT_MIN_VALUE, FLOAT_MAX_VALUE)
        location_id = self.location_use_case.create(self.world_id, **anon_create_location_kwargs(
            span=PositionalRange(latitude=large_range, longitude=large_range, altitude=large_range, continuum=large_range, reality={0})
        ), profile=self.profile).id
        cont_1 = Range(FLOAT_MIN_VALUE, -56.)
        cont_2 = Range(-58., -20.)
        cont_3 = Range(-19., 20.)
        cont_4 = Range(-18., 20.)
        cont_5 = Range(22., 42.)
        cont_6 = Range(22., 43.)
        cont_7 = Range(25., FLOAT_MAX_VALUE)
        event_1 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_1, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        event_5 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_5, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        event_3 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_3, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        event_6 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_6, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        event_4 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_4, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        event_7 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_7, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        event_2 = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(
                span=anon_positional_range(continuum=cont_2, reality={0}), affected_locations={location_id}),
            profile=self.profile)
        events = [event_1, event_2, event_3, event_4, event_5, event_6, event_7]
        expected_timeline = [event.id for event in events]

        # Act
        actual = self.timeline_use_case.construct_location_timeline(self.world_id, location_id, profile=self.profile)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__construct_location_timeline__should_delegate_to_filter_tagged_entities__when_filtering_necessary(
            self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        span = anon_positional_range()

        location = self.location_use_case.create(self.world_id, **anon_create_location_kwargs(span=span), profile=self.profile)
        event = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(span=span, affected_locations={location.id}), profile=self.profile)

        filter_tagged_entities_mock.return_value = {event}, {}
        expected_input = {event}
        expected_output = [event.id]

        # Act
        actual = self.timeline_use_case.construct_location_timeline(self.world_id, location.id, profile=self.profile)

        # Assert
        filter_tagged_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)

    def test__construct_traveler_timeline__should_reject_nonexistent_world(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(self.world_id, **anon_create_traveler_kwargs(), profile=self.profile)
        non_existent_world_id = anon_prefixed_id(prefix="world")

        # Act
        def action(): self.timeline_use_case.construct_traveler_timeline(non_existent_world_id, traveler.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_traveler_timeline__should_reject_nonexistent_traveler(self) -> None:
        # Arrange
        traveler_id = anon_prefixed_id(prefix="traveler")

        # Act
        def action(): self.timeline_use_case.construct_traveler_timeline(self.world_id, traveler_id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_traveler_timeline__should_reject_existent_traveler_associated_with_another_world(self) -> None:
        # Arrange
        traveler = self.traveler_use_case.create(self.world_id, **anon_create_traveler_kwargs(), profile=self.profile)

        # Act
        def action(): self.timeline_use_case.construct_traveler_timeline(self.other_world_id, traveler.id, profile=self.profile)

        # Assert
        self.assertRaises(NameError, action)

    def test__construct_traveler_timeline__should_return_same_event_multiple_times_when_travelers_journey_intersects_it_multiple_times(
            self) -> None:
        # Arrange
        initially_on_ground = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0), movement_type=MovementType.IMMEDIATE)
        jumping_upward = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=5, continuum=2, reality=0), movement_type=MovementType.INTERPOLATED)
        jump_peak = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=10, continuum=3, reality=0), movement_type=MovementType.INTERPOLATED)
        falling_downward = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=5, continuum=4, reality=0), movement_type=MovementType.INTERPOLATED)
        back_on_ground = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=0, continuum=5, reality=0), movement_type=MovementType.INTERPOLATED)

        near_ground_span = PositionalRange(
            latitude=Range(-2, 2), longitude=Range(-2, 2), altitude=Range(-2, 2), continuum=Range(0, 5), reality={0})
        in_air_span = PositionalRange(
            latitude=Range(-2, 2), longitude=Range(-2, 2), altitude=Range(8, 12), continuum=Range(0, 5), reality={0})

        traveler = self.traveler_use_case.create(self.world_id, **anon_create_traveler_kwargs(journey=[
            initially_on_ground,
            jumping_upward,
            jump_peak,
            falling_downward,
            back_on_ground,
        ]), profile=self.profile)
        on_ground_event = self.event_use_case.create(self.world_id, **anon_create_event_kwargs(
            span=near_ground_span, affected_travelers={traveler.id}), profile=self.profile)
        in_air_event = self.event_use_case.create(self.world_id, **anon_create_event_kwargs(
            span=in_air_span, affected_travelers={traveler.id}), profile=self.profile)

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
        actual = self.timeline_use_case.construct_traveler_timeline(self.world_id, traveler.id, profile=self.profile)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    def test__construct_traveler_timeline__should_put_affecting_events_after_the_position__when_movement_type_is_immediate(self) -> None:
        # Arrange
        outside_affected_area = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0), movement_type=MovementType.IMMEDIATE)
        inside_affected_area = PositionalMove(
            position=Position(latitude=5, longitude=1, altitude=0, continuum=2, reality=0), movement_type=MovementType.IMMEDIATE)

        affected_area = PositionalRange(
            latitude=Range(4, 6), longitude=Range(1, 1), altitude=Range(0, 0), continuum=Range(0, 3), reality={0})

        traveler = self.traveler_use_case.create(self.world_id, **anon_create_traveler_kwargs(journey=[
            outside_affected_area,
            inside_affected_area,
        ]), profile=self.profile)
        event = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(span=affected_area, affected_travelers={traveler.id}), profile=self.profile)

        expected_timeline = [
            outside_affected_area,
            inside_affected_area,
            event.id,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(self.world_id, traveler.id, profile=self.profile)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    def test__construct_traveler_timeline__should_put_affecting_events_before_the_position__when_movement_type_is_interpolated(self) \
            -> None:
        # Arrange
        outside_affected_area = PositionalMove(
            position=Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0), movement_type=MovementType.IMMEDIATE)
        inside_affected_area = PositionalMove(
            position=Position(latitude=5, longitude=1, altitude=0, continuum=2, reality=0), movement_type=MovementType.INTERPOLATED)

        affected_area = PositionalRange(
            latitude=Range(4, 6), longitude=Range(1, 1), altitude=Range(0, 0), continuum=Range(0, 3), reality={0})

        traveler = self.traveler_use_case.create(self.world_id, **anon_create_traveler_kwargs(journey=[
            outside_affected_area,
            inside_affected_area,
        ]), profile=self.profile)
        event = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(span=affected_area, affected_travelers={traveler.id}), profile=self.profile)

        expected_timeline = [
            outside_affected_area,
            event.id,
            inside_affected_area,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(self.world_id, traveler.id, profile=self.profile)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    def test__construct_traveler_timeline__should_not_report_same_event_multiple_times__when_traveler_does_not_leave_events_span(
            self) -> None:
        # Arrange
        pos_1_outside_affected_area = Position(latitude=1, longitude=1, altitude=0, continuum=1, reality=0)
        pos_2_inside_affected_area_a = Position(latitude=5, longitude=1, altitude=0, continuum=2, reality=0)
        pos_3_inside_affected_area_b = Position(latitude=6, longitude=1, altitude=0, continuum=3, reality=0)
        pos_4_inside_affected_area_a = Position(latitude=5, longitude=1, altitude=0, continuum=4, reality=0)
        pos_5_outside_affected_area = Position(latitude=1, longitude=1, altitude=0, continuum=5, reality=0)
        pos_6_inside_affected_area_b = Position(latitude=6, longitude=1, altitude=0, continuum=6, reality=0)
        pos_mov_1_outside_affected_area = PositionalMove(position=pos_1_outside_affected_area, movement_type=MovementType.IMMEDIATE)
        pos_mov_2_inside_affected_area_a = PositionalMove(position=pos_2_inside_affected_area_a, movement_type=MovementType.INTERPOLATED)
        pos_mov_3_inside_affected_area_b = PositionalMove(position=pos_3_inside_affected_area_b, movement_type=MovementType.INTERPOLATED)
        pos_mov_4_inside_affected_area_a = PositionalMove(position=pos_4_inside_affected_area_a, movement_type=MovementType.IMMEDIATE)
        pos_mov_5_outside_affected_area = PositionalMove(position=pos_5_outside_affected_area, movement_type=MovementType.INTERPOLATED)
        pos_mov_6_inside_affected_area_b = PositionalMove(position=pos_6_inside_affected_area_b, movement_type=MovementType.INTERPOLATED)

        affected_area = PositionalRange(latitude=Range(4, 6), longitude=Range(1, 1), altitude=Range(0, 0), continuum=Range(0, 6),
                                        reality={0})

        traveler = self.traveler_use_case.create(self.world_id, **anon_create_traveler_kwargs(journey=[
            pos_mov_1_outside_affected_area,
            pos_mov_2_inside_affected_area_a,
            pos_mov_3_inside_affected_area_b,
            pos_mov_4_inside_affected_area_a,
            pos_mov_5_outside_affected_area,
            pos_mov_6_inside_affected_area_b,
        ]), profile=self.profile)
        event = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(span=affected_area, affected_travelers={traveler.id}), profile=self.profile)

        expected_timeline = [
            pos_mov_1_outside_affected_area,
            event.id,
            pos_mov_2_inside_affected_area_a,
            pos_mov_3_inside_affected_area_b,
            pos_mov_4_inside_affected_area_a,
            pos_mov_5_outside_affected_area,
            event.id,
            pos_mov_6_inside_affected_area_b,
        ]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(self.world_id, traveler.id, profile=self.profile)

        # Assert
        self.assertListEqual(expected_timeline, actual)

    @patch("application.use_case.filtering_use_cases.FilteringUseCase.filter_tagged_entities")
    def test__construct_traveler_timeline__should_delegate_to_filter_tagged_entities__when_filtering_necessary(
            self, filter_tagged_entities_mock: MagicMock) -> None:
        # Arrange
        span = anon_positional_range()
        position = Position(latitude=span.latitude.low, longitude=span.longitude.low, altitude=span.altitude.low,
                            continuum=span.continuum.low, reality=next(iter(span.reality)))
        positional_move = PositionalMove(position=position, movement_type=MovementType.IMMEDIATE)
        traveler = self.traveler_use_case.create(
            self.world_id, **anon_create_traveler_kwargs(journey=[positional_move]), profile=self.profile)
        event = self.event_use_case.create(
            self.world_id, **anon_create_event_kwargs(span=span, affected_travelers={traveler.id}), profile=self.profile)

        filter_tagged_entities_mock.return_value = {event}, {}
        expected_input = {event}
        expected_output = [positional_move, event.id]

        # Act
        actual = self.timeline_use_case.construct_traveler_timeline(self.world_id, traveler.id, profile=self.profile)

        # Assert
        filter_tagged_entities_mock.assert_called_once_with(expected_input)
        self.assertEqual(expected_output, actual)
