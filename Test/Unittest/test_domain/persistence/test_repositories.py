from abc import ABC, abstractmethod
from typing import Callable, Any, Collection

from Test.Unittest.test_helpers.anons import anon_location, anon_anything, anon_traveler, anon_event, anon_positional_range, anon_world
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import WorldRepository, LocationRepository, TravelerRepository, EventRepository
from domain.positions import PositionalMove, Position, MovementType
from domain.travelers import Traveler
from domain.worlds import World
from test_helpers.anons import anon_prefixed_id


class TestSRDRepository(ABC):
    assertIsNone: Callable
    assertEqual: Callable
    assertSetEqual: Callable
    assertRaises: Callable

    @property
    @abstractmethod
    def repository(self) -> Any:
        pass

    @property
    @abstractmethod
    def preceding_ids(self) -> Collection[Any]:
        pass

    @abstractmethod
    def anon_entity(self) -> Any:
        pass

    @abstractmethod
    def get_entity_identifier(self, entity: Any) -> Any:
        pass

    def test__save__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = anon_anything(not_type=Location)

        # Act
        def action(): self.repository.save(*self.preceding_ids, invalid_type)

        # Assert
        self.assertRaises(TypeError, action)

    def test__save__should_not_throw_exception__when_storing_valid_entity(self) -> None:
        # Arrange
        entity = self.anon_entity()

        # Act
        self.repository.save(*self.preceding_ids, entity)

        # Assert

    def test__retrieve__should_reject_invalid_types(self) -> None:
        # Arrange
        valid_type = type(self.get_entity_identifier(self.anon_entity()))
        invalid_type = anon_anything(not_type=valid_type)

        # Act
        def action(): self.repository.retrieve(*self.preceding_ids, invalid_type)

        # Assert
        self.assertRaises(TypeError, action)

    def test__retrieve__should_raise_exception__when_no_stored_entity_matches_the_given_identifier(self) -> None:
        # Arrange
        anon_identifier = self.get_entity_identifier(self.anon_entity())

        # Act
        def action(): self.repository.retrieve(*self.preceding_ids, anon_identifier)

        # Assert
        self.assertRaises(NameError, action)

    def test__retrieve__should_return_saved_entity__when_stored_entity_matches_the_given_identifier(self) -> None:
        # Arrange
        expected_entity = self.anon_entity()
        entity_identifier = self.get_entity_identifier(expected_entity)
        self.repository.save(*self.preceding_ids, expected_entity)

        # Act
        actual = self.repository.retrieve(*self.preceding_ids, entity_identifier)

        # Assert
        self.assertEqual(expected_entity, actual)

    def test__retrieve_all__should_return_empty_set__when_no_entities_stored(self) -> None:
        # Arrange
        expected = set()

        # Act
        actual = self.repository.retrieve_all(*self.preceding_ids)

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_stored_entities__when_entities_stored(self) -> None:
        # Arrange
        expected = {self.anon_entity(), self.anon_entity()}
        for entity in expected:
            self.repository.save(*self.preceding_ids, entity)

        # Act
        actual = self.repository.retrieve_all(*self.preceding_ids)

        # Assert
        self.assertSetEqual(expected, actual)
        
    def test__retrieve_all__should_not_return_deleted_entities__when_previously_existing_entities_are_deleted(self) -> None:
        # Arrange
        entity = self.anon_entity()
        self.repository.save(*self.preceding_ids, entity)
        self.repository.delete(*self.preceding_ids, entity.id)

        # Act
        actual = self.repository.retrieve_all(*self.preceding_ids)

        # Assert
        self.assertSetEqual(set(), actual)

    def test__delete__should_delete_entity__when_matching_entity_stored(self) -> None:
        # Arrange
        entity = self.anon_entity()
        entity_identifier = self.get_entity_identifier(entity)
        self.repository.save(*self.preceding_ids, entity)

        # Act
        self.repository.delete(*self.preceding_ids, entity_identifier)

        # Assert
        self.assertRaises(NameError, lambda: self.repository.retrieve(*self.preceding_ids, entity_identifier))

    def test__delete__should_raise_exception__when_no_matching_entity_stored(self) -> None:
        # Arrange
        anon_entity_identifier = self.get_entity_identifier(self.anon_entity())

        # Act
        def action(): self.repository.delete(*self.preceding_ids, anon_entity_identifier)

        # Assert
        self.assertRaises(NameError, action)


class TestWorldsRepository(TestSRDRepository):
    @property
    @abstractmethod
    def repository(self) -> WorldRepository:
        pass

    @property
    def preceding_ids(self) -> Collection[Any]:
        return []

    def anon_entity(self) -> World:
        return anon_world()

    def get_entity_identifier(self, entity: World) -> PrefixedUUID:
        return entity.id


class TestLocationsRepository(TestSRDRepository):
    _world_id: PrefixedUUID = anon_prefixed_id(prefix="world")

    @property
    @abstractmethod
    def repository(self) -> LocationRepository:
        pass

    @property
    def preceding_ids(self) -> Collection[Any]:
        return [self._world_id]

    def anon_entity(self) -> Location:
        return anon_location()

    def get_entity_identifier(self, entity: Location) -> PrefixedUUID:
        return entity.id


class TestTravelerRepository(TestSRDRepository):
    _world_id: PrefixedUUID = anon_prefixed_id(prefix="world")

    @property
    @abstractmethod
    def repository(self) -> TravelerRepository:
        pass

    @property
    def preceding_ids(self) -> Collection[Any]:
        return [self._world_id]

    def anon_entity(self) -> Traveler:
        return anon_traveler()

    def get_entity_identifier(self, entity: Traveler) -> PrefixedUUID:
        return entity.id


class TestEventRepository(TestSRDRepository):
    _world_id: PrefixedUUID = anon_prefixed_id(prefix="world")

    @property
    @abstractmethod
    def repository(self) -> EventRepository:
        pass

    @property
    def preceding_ids(self) -> Collection[Any]:
        return [self._world_id]

    def anon_entity(self) -> Event:
        return anon_event()

    def get_entity_identifier(self, entity: Event) -> PrefixedUUID:
        return entity.id

    def test__retrieve_all__should_return_events_affecting_location__when_location_id_provided(self) -> None:
        # Arrange
        span = anon_positional_range()
        location = anon_location(span=span)
        linked_event = anon_event(span=span, affected_locations={location.id})
        other_event = anon_event()
        self.repository.save(*self.preceding_ids, event=linked_event)
        self.repository.save(*self.preceding_ids, event=other_event)
        expected = {linked_event}

        # Act
        actual = self.repository.retrieve_all(*self.preceding_ids, location_id=location.id)

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_events_affecting_traveler__when_traveler_id_provided(self) -> None:
        # Arrange
        span = anon_positional_range()
        journey = [PositionalMove(
            position=Position(latitude=span.latitude.low, longitude=span.longitude.low, altitude=span.altitude.low,
                              continuum=span.continuum.low, reality=next(iter(span.reality))), movement_type=MovementType.IMMEDIATE)]
        traveler = anon_traveler(journey=journey)
        linked_event = anon_event(span=span, affected_travelers={traveler.id})
        other_event = anon_event()
        self.repository.save(*self.preceding_ids, event=linked_event)
        self.repository.save(*self.preceding_ids, event=other_event)
        expected = {linked_event}

        # Act
        actual = self.repository.retrieve_all(*self.preceding_ids, traveler_id=traveler.id)

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_events_affecting_location_and_traveler__when_location_and_traveler_id_provided(self) -> None:
        # Arrange
        span = anon_positional_range()
        journey = [PositionalMove(
            position=Position(latitude=span.latitude.low, longitude=span.longitude.low, altitude=span.altitude.low,
                              continuum=span.continuum.low, reality=next(iter(span.reality))), movement_type=MovementType.IMMEDIATE)]
        traveler = anon_traveler(journey=journey)
        location = anon_location(span=span)

        linked_event_traveler_only = anon_event(span=span, affected_travelers={traveler.id})
        linked_event_location_only = anon_event(span=span, affected_locations={location.id})
        linked_event_both = anon_event(span=span, affected_travelers={traveler.id}, affected_locations={location.id})
        self.repository.save(*self.preceding_ids, event=linked_event_traveler_only)
        self.repository.save(*self.preceding_ids, event=linked_event_location_only)
        self.repository.save(*self.preceding_ids, event=linked_event_both)
        expected = {linked_event_both}

        # Act
        actual = self.repository.retrieve_all(*self.preceding_ids, location_id=location.id, traveler_id=traveler.id)

        # Assert
        self.assertSetEqual(expected, actual)
