from typing import Set
from uuid import uuid4

from application.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository
from domain.positions import PositionalRange
from domain.tags import Tag


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

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        if not location_id.prefix == "location":
            raise ValueError("Argument 'location_id' must be prefixed with 'location'")

        return self._location_repository.retrieve(location_id)

    def retrieve_all(self, **kwargs) -> Set[Location]:
        all_locations = self._location_repository.retrieve_all()
        name_filtered_locations, kwargs = FilteringUseCase.filter_named_entities(all_locations, **kwargs)
        tag_filtered_locations, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_locations, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return tag_filtered_locations

    def update(self, location_id: PrefixedUUID, *,
               name: str = None, description: str = None, span: PositionalRange = None, tags: Set[Tag] = None) -> Location:

        existing_location = self._location_repository.retrieve(location_id)

        updated_location = Location(
            id=location_id,
            name=name if name is not None else existing_location.name,
            description=description if description is not None else existing_location.description,
            span=span if span is not None else existing_location.span,
            tags=tags if tags is not None else existing_location.tags,
        )
        self._location_repository.save(updated_location)
        return updated_location

    def delete(self, location_id: PrefixedUUID) -> None:
        if not location_id.prefix == "location":
            raise ValueError("Argument 'location_id' must be prefixed with 'location'")

        return self._location_repository.delete(location_id)
