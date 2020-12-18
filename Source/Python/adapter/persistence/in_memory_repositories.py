from copy import deepcopy
from typing import Set, Dict, TypeVar, Generic, Type

from domain.events import Event
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository
from domain.travelers import Traveler


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

    def __init__(self) -> None:
        self._inner_repo = _InMemoryIdentifiedEntityRepository(Event)

    def save(self, event: Event) -> None:
        self._inner_repo.save(event)

    def retrieve(self, event_id: PrefixedUUID) -> Event:
        return self._inner_repo.retrieve(event_id)

    def retrieve_all(self) -> Set[Event]:
        return self._inner_repo.retrieve_all()

    def delete(self, event_id: PrefixedUUID) -> None:
        return self._inner_repo.delete(event_id)
