from copy import deepcopy
from typing import Set, Optional, Dict

from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository


class InMemoryLocationRepository(LocationRepository):
    _locations_by_id: Dict[PrefixedUUID, Location]

    def __init__(self):
        self._locations_by_id = {}

    def save(self, location: Location) -> None:
        if not isinstance(location, Location):
            raise TypeError(f"Argument 'location' must be of type {Location}")

        self._locations_by_id[location.id] = location

    def retrieve(self, location_id: PrefixedUUID) -> Optional[Location]:
        if not isinstance(location_id, PrefixedUUID):
            raise TypeError(f"Argument 'location_id' must be of type {PrefixedUUID}")

        return deepcopy(self._locations_by_id.get(location_id, None))

    def retrieve_all(self) -> Set[Location]:
        return {
            deepcopy(location)
            for location in self._locations_by_id.values()
        }
