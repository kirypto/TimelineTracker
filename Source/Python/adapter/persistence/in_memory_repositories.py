from collections import defaultdict
from copy import deepcopy
from typing import Set, Dict, TypeVar, Generic, Type

from domain.events import Event
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository, WorldRepository
from domain.travelers import Traveler
from domain.worlds import World


_T = TypeVar('_T', bound=IdentifiedEntity)


class _InMemoryIdentifiedEntityRepository(Generic[_T]):
    _entity_type: Type[_T]
    _entities_by_id: Dict[PrefixedUUID, _T]

    def __init__(self, entity_type: Type[_T]) -> None:
        self._entity_type = entity_type
        self._entities_by_id = {}

    def save(self, entity: _T) -> None:
        if not isinstance(entity, self._entity_type):
            raise TypeError(f"Argument 'entity' must be of type {_T}")

        self._entities_by_id[entity.id] = entity

    def retrieve(self, entity_id: PrefixedUUID) -> _T:
        if not isinstance(entity_id, PrefixedUUID):
            raise TypeError(f"Argument 'entity_id' must be of type {PrefixedUUID}")
        if entity_id not in self._entities_by_id:
            raise NameError(f"No stored entity with id '{entity_id}'")

        return deepcopy(self._entities_by_id[entity_id])

    def retrieve_all(self) -> Set[_T]:
        return {
            deepcopy(entity)
            for entity in self._entities_by_id.values()
        }

    def delete(self, entity_id: PrefixedUUID) -> None:
        if entity_id not in self._entities_by_id:
            raise NameError(f"No stored entity with id '{entity_id}'")

        self._entities_by_id.pop(entity_id)


class InMemoryWorldRepository(WorldRepository):
    _inner_repo: _InMemoryIdentifiedEntityRepository

    def __init__(self) -> None:
        self._inner_repo = _InMemoryIdentifiedEntityRepository(World)

    def save(self, world: World) -> None:
        self._inner_repo.save(world)

    def retrieve(self, world_id: PrefixedUUID) -> World:
        return self._inner_repo.retrieve(world_id)

    def retrieve_all(self) -> Set[World]:
        return self._inner_repo.retrieve_all()

    def delete(self, world_id: PrefixedUUID) -> None:
        return self._inner_repo.delete(world_id)


class InMemoryLocationRepository(LocationRepository):
    _inner_repo: _InMemoryIdentifiedEntityRepository

    def __init__(self) -> None:
        self._inner_repo = _InMemoryIdentifiedEntityRepository(Location)

    def save(self, location: Location) -> None:
        self._inner_repo.save(location)

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        return self._inner_repo.retrieve(location_id)

    def retrieve_all(self) -> Set[Location]:
        return self._inner_repo.retrieve_all()

    def delete(self, location_id: PrefixedUUID) -> None:
        return self._inner_repo.delete(location_id)


class InMemoryTravelerRepository(TravelerRepository):
    _inner_repo: _InMemoryIdentifiedEntityRepository

    def __init__(self) -> None:
        self._inner_repo = _InMemoryIdentifiedEntityRepository(Traveler)

    def save(self, traveler: Traveler) -> None:
        self._inner_repo.save(traveler)

    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        return self._inner_repo.retrieve(traveler_id)

    def retrieve_all(self) -> Set[Traveler]:
        return self._inner_repo.retrieve_all()

    def delete(self, traveler_id: PrefixedUUID) -> None:
        return self._inner_repo.delete(traveler_id)


class InMemoryEventRepository(EventRepository):
    _inner_repo: _InMemoryIdentifiedEntityRepository
    _event_ids_by_location_id: Dict[PrefixedUUID, Set[PrefixedUUID]]
    _event_ids_by_traveler_id: Dict[PrefixedUUID, Set[PrefixedUUID]]

    def __init__(self) -> None:
        self._inner_repo = _InMemoryIdentifiedEntityRepository(Event)
        self._event_ids_by_location_id = defaultdict(set)
        self._event_ids_by_traveler_id = defaultdict(set)

    def save(self, event: Event) -> None:
        self._inner_repo.save(event)
        for location_id in event.affected_locations:
            self._event_ids_by_location_id[location_id].add(event.id)
        for traveler_id in event.affected_travelers:
            self._event_ids_by_traveler_id[traveler_id].add(event.id)

    def retrieve(self, event_id: PrefixedUUID) -> Event:
        return self._inner_repo.retrieve(event_id)

    def retrieve_all(self, *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None) -> Set[Event]:
        if location_id is None and traveler_id is None:
            # Neither filter provided, return all
            return self._inner_repo.retrieve_all()

        events_linked_to_provided_location_id = self._event_ids_by_location_id.get(location_id, set())
        events_linked_to_provided_traveler_id = self._event_ids_by_traveler_id.get(traveler_id, set())
        if location_id is not None and traveler_id is not None:
            # Both filters provided, return events linked to both
            desired_event_ids = events_linked_to_provided_location_id.intersection(events_linked_to_provided_traveler_id)
        else:
            # Only on filter provided, return events linked to that one (union with empty set)
            desired_event_ids = events_linked_to_provided_location_id.union(events_linked_to_provided_traveler_id)
        return {self.retrieve(event_id) for event_id in desired_event_ids}

    def delete(self, event_id: PrefixedUUID) -> None:
        self._inner_repo.delete(event_id)
        for location_id in self._event_ids_by_location_id:
            self._event_ids_by_location_id[location_id].remove(event_id)
        for traveler_id in self._event_ids_by_traveler_id:
            self._event_ids_by_traveler_id[traveler_id].remove(event_id)


location_repository_class = InMemoryLocationRepository
traveler_repository_class = InMemoryTravelerRepository
event_repository_class = InMemoryEventRepository
