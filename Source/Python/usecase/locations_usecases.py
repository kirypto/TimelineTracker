from typing import Set, Optional
from uuid import uuid4

from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository


class LocationUseCase:
    _location_repository: LocationRepository

    def __init__(self, location_repository: LocationRepository) -> None:
        if not isinstance(location_repository, LocationRepository):
            raise TypeError(f"Argument 'location_repository' must be of type {LocationRepository}")

        self._location_repository = location_repository

    def create(self, **kwargs) -> Location:
        kwargs["id"] = PrefixedUUID("location", uuid4())
        location = Location(**kwargs)

        self._location_repository.save(location)

        return location

    def retrieve(self, location_id: PrefixedUUID) -> Optional[Location]:
        if not isinstance(location_id, PrefixedUUID):
            raise TypeError(f"Argument 'location_id' must be of type {PrefixedUUID}")
        if not location_id.prefix == "location":
            raise ValueError("Argument 'location_id' must be prefixed with 'location'")

        return self._location_repository.retrieve(location_id)

    def retrieve_all(self) -> Set[Location]:
        return self._location_repository.retrieve_all()
