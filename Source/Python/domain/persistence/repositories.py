from abc import ABC, abstractmethod
from typing import Set

from domain.events import Event
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.travelers import Traveler
from domain.worlds import World


class WorldRepository(ABC):
    @abstractmethod
    def save(self, world: World) -> None:
        pass

    @abstractmethod
    def retrieve(self, world_id: PrefixedUUID) -> World:
        pass

    @abstractmethod
    def retrieve_all(self) -> Set[World]:
        pass

    @abstractmethod
    def delete(self, world_id: PrefixedUUID) -> None:
        pass


class LocationRepository(ABC):
    @abstractmethod
    def save(self, world_id: PrefixedUUID, location: Location) -> None:
        pass

    @abstractmethod
    def retrieve(self, world_id: PrefixedUUID, location_id: PrefixedUUID) -> Location:
        pass

    @abstractmethod
    def retrieve_all(self, world_id: PrefixedUUID) -> Set[Location]:
        pass

    @abstractmethod
    def delete(self, world_id: PrefixedUUID, location_id: PrefixedUUID) -> None:
        pass


class TravelerRepository(ABC):
    @abstractmethod
    def save(self, world_id: PrefixedUUID, traveler: Traveler) -> None:
        pass

    @abstractmethod
    def retrieve(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> Traveler:
        pass

    @abstractmethod
    def retrieve_all(self, world_id: PrefixedUUID) -> Set[Traveler]:
        pass

    @abstractmethod
    def delete(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> None:
        pass


class EventRepository(ABC):
    @abstractmethod
    def save(self, world_id: PrefixedUUID, event: Event) -> None:
        pass

    @abstractmethod
    def retrieve(self, world_id: PrefixedUUID, event_id: PrefixedUUID) -> Event:
        pass

    @abstractmethod
    def retrieve_all(self, world_id: PrefixedUUID, *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None) -> Set[Event]:
        pass

    @abstractmethod
    def delete(self, world_id: PrefixedUUID, event_id: PrefixedUUID) -> None:
        pass
