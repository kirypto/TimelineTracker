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

    @abstractmethod
    def associate(
            self, world_id: PrefixedUUID,
            *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None, event_id: PrefixedUUID = None
    ) -> None:
        pass

    @abstractmethod
    def disassociate(
            self, world_id: PrefixedUUID,
            *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None, event_id: PrefixedUUID = None
    ) -> None:
        pass

    @abstractmethod
    def get_all_associated(
            self, world_id: PrefixedUUID, *, locations: bool = False, travelers: bool = False, events: bool = False
    ) -> Set[PrefixedUUID]:
        pass


class LocationRepository(ABC):
    @abstractmethod
    def save(self, location: Location) -> None:
        pass

    @abstractmethod
    def retrieve(self, location_id: PrefixedUUID) -> Location:
        pass

    @abstractmethod
    def retrieve_all(self) -> Set[Location]:
        pass

    @abstractmethod
    def delete(self, location_id: PrefixedUUID) -> None:
        pass


class TravelerRepository(ABC):
    @abstractmethod
    def save(self, traveler: Traveler) -> None:
        pass

    @abstractmethod
    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        pass

    @abstractmethod
    def retrieve_all(self) -> Set[Traveler]:
        pass

    @abstractmethod
    def delete(self, traveler_id: PrefixedUUID) -> None:
        pass


class EventRepository(ABC):
    @abstractmethod
    def save(self, event: Event) -> None:
        pass

    @abstractmethod
    def retrieve(self, event_id: PrefixedUUID) -> Event:
        pass

    @abstractmethod
    def retrieve_all(self, *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None) -> Set[Event]:
        pass

    @abstractmethod
    def delete(self, event_id: PrefixedUUID) -> None:
        pass
