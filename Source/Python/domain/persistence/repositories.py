from abc import ABC, abstractmethod
from typing import Set

from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.travelers import Traveler


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
