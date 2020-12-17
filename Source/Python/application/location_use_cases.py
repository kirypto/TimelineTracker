from typing import Set
from uuid import uuid4

from application.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, EventRepository


class LocationUseCase:
    _location_repository: LocationRepository
    _event_repository: EventRepository

    def __init__(self, location_repository: LocationRepository, event_repository: EventRepository) -> None:
        if not isinstance(location_repository, LocationRepository):
            raise TypeError(f"Argument 'location_repository' must be of type {LocationRepository}")
        if not isinstance(event_repository, EventRepository):
            raise TypeError(f"Argument 'event_repository' must be of type {EventRepository}")

        self._location_repository = location_repository
        self._event_repository = event_repository

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
        span_filtered_locations, kwargs = FilteringUseCase.filter_spanning_entities(tag_filtered_locations, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return span_filtered_locations

    def update(self, location_id: PrefixedUUID, **kwargs) -> Location:
        if "id" in kwargs:
            raise ValueError(f"Cannot update 'id' attribute of {Location.__name__}")
        existing_location = self._location_repository.retrieve(location_id)
        updated_location = Location(
            id=location_id,
            name=kwargs.pop("name") if "name" in kwargs else existing_location.name,
            description=kwargs.pop("description") if "description" in kwargs else existing_location.description,
            span=kwargs.pop("span") if "span" in kwargs else existing_location.span,
            tags=kwargs.pop("tags") if "tags" in kwargs else existing_location.tags,
            **kwargs
        )

        self._validate_linked_events_still_intersect_for_update(updated_location)

        self._location_repository.save(updated_location)
        return updated_location

    def delete(self, location_id: PrefixedUUID) -> None:
        if not location_id.prefix == "location":
            raise ValueError("Argument 'location_id' must be prefixed with 'location'")

        self._validate_no_linked_events_for_delete(location_id)

        return self._location_repository.delete(location_id)

    def _validate_no_linked_events_for_delete(self, location_id) -> None:
        all_events = self._event_repository.retrieve_all()
        linked_event_ids = [str(event.id) for event in all_events if location_id in event.affected_locations]
        if linked_event_ids:
            raise ValueError(f"Cannot delete location, currently linked to the following Events {','.join(linked_event_ids)}")

    def _validate_linked_events_still_intersect_for_update(self, updated_location: Location) -> None:
        all_events = self._event_repository.retrieve_all()
        linked_events = [event for event in all_events if updated_location.id in event.affected_locations]
        for linked_event in linked_events:
            if not linked_event.span.intersects(updated_location.span):
                raise ValueError(f"Cannot modify location, currently linked to Event {linked_event.id} and the modification would cause them to no "
                                 f"longer intersect")
