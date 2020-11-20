from copy import deepcopy
from typing import Set, Dict

from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository
from domain.travelers import Traveler


class InMemoryLocationRepository(LocationRepository):
    _locations_by_id: Dict[PrefixedUUID, Location]

    def __init__(self) -> None:
        self._locations_by_id = {}

    def save(self, location: Location) -> None:
        if not isinstance(location, Location):
            raise TypeError(f"Argument 'location' must be of type {Location}")

        self._locations_by_id[location.id] = location

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        if not isinstance(location_id, PrefixedUUID):
            raise TypeError(f"Argument 'location_id' must be of type {PrefixedUUID}")
        if location_id not in self._locations_by_id:
            raise NameError(f"No stored location with id '{location_id}'")

        return deepcopy(self._locations_by_id[location_id])

    def retrieve_all(self) -> Set[Location]:
        return {
            deepcopy(location)
            for location in self._locations_by_id.values()
        }

    def delete(self, location_id: PrefixedUUID) -> None:
        if location_id not in self._locations_by_id:
            raise NameError(f"No stored location with id '{location_id}'")

        self._locations_by_id.pop(location_id)


class InMemoryTravelerRepository(TravelerRepository):
    _travelers_by_id: Dict[PrefixedUUID, Traveler]

    def __init__(self) -> None:
        self._travelers_by_id = {}

    def save(self, traveler: Traveler) -> None:
        if not isinstance(traveler, Traveler):
            raise TypeError(f"Argument 'traveler' must be of type {Traveler}")

        self._travelers_by_id[traveler.id] = traveler

    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        if not isinstance(traveler_id, PrefixedUUID):
            raise TypeError(f"Argument 'traveler_id' must be of type {PrefixedUUID}")
        if traveler_id not in self._travelers_by_id:
            raise NameError(f"No stored traveler with id '{traveler_id}'")

        return deepcopy(self._travelers_by_id[traveler_id])

    def retrieve_all(self) -> Set[Traveler]:
        return {
            deepcopy(traveler)
            for traveler in self._travelers_by_id.values()
        }

    def delete(self, traveler_id: PrefixedUUID) -> None:
        if traveler_id not in self._travelers_by_id:
            raise NameError(f"No stored traveler with id '{traveler_id}'")

        self._travelers_by_id.pop(traveler_id)
