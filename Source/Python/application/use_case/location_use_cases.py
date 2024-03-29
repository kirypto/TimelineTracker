from typing import Set

from application.access.authentication import requires_authentication
from application.use_case.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID, generate_prefixed_id
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, EventRepository, WorldRepository


class LocationUseCase:
    _world_repository: WorldRepository
    _location_repository: LocationRepository
    _event_repository: EventRepository

    def __init__(
            self, world_repository: WorldRepository, location_repository: LocationRepository, event_repository: EventRepository
    ) -> None:
        self._world_repository = world_repository
        self._location_repository = location_repository
        self._event_repository = event_repository

    @requires_authentication()
    def create(self, world_id: PrefixedUUID, **kwargs) -> Location:
        self._validate_world_exists(world_id)
        kwargs["id"] = generate_prefixed_id("location")
        location = Location(**kwargs)

        self._location_repository.save(location)
        self._world_repository.associate(world_id, location_id=location.id)

        return location

    @requires_authentication()
    def retrieve(self, world_id: PrefixedUUID, location_id: PrefixedUUID) -> Location:
        self._validate_world_exists(world_id)
        if not location_id.prefix == "location":
            raise ValueError("Argument 'location_id' must be prefixed with 'location'")
        associated_locations = self._world_repository.get_all_associated(world_id, locations=True)
        if location_id not in associated_locations:
            raise NameError(f"No location '{location_id}' is exists for world '{world_id}'")

        return self._location_repository.retrieve(location_id)

    @requires_authentication()
    def retrieve_all(self, world_id: PrefixedUUID, **kwargs) -> Set[Location]:
        self._validate_world_exists(world_id)
        associated_locations = self._world_repository.get_all_associated(world_id, locations=True)
        all_locations = {location for location in self._location_repository.retrieve_all() if location.id in associated_locations}
        name_filtered_locations, kwargs = FilteringUseCase.filter_named_entities(all_locations, **kwargs)
        tag_filtered_locations, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_locations, **kwargs)
        span_filtered_locations, kwargs = FilteringUseCase.filter_spanning_entities(tag_filtered_locations, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return span_filtered_locations

    @requires_authentication()
    def update(self, world_id: PrefixedUUID, location: Location) -> None:
        self._validate_world_exists(world_id)
        associated_locations = self._world_repository.get_all_associated(world_id, locations=True)
        if location.id not in associated_locations:
            raise NameError(f"No location '{location.id}' is exists for world '{world_id}'")

        self._location_repository.retrieve(location.id)
        self._validate_linked_events_still_intersect_for_update(location)

        self._location_repository.save(location)

    @requires_authentication()
    def delete(self, world_id: PrefixedUUID, location_id: PrefixedUUID) -> None:
        self._validate_world_exists(world_id)
        if not location_id.prefix == "location":
            raise ValueError("Argument 'location_id' must be prefixed with 'location'")
        associated_locations = self._world_repository.get_all_associated(world_id, locations=True)
        if location_id not in associated_locations:
            raise NameError(f"No location '{location_id}' is exists for world '{world_id}'")

        self._validate_no_linked_events_for_delete(location_id)

        return self._location_repository.delete(location_id)

    def _validate_world_exists(self, world_id: PrefixedUUID) -> None:
        if not world_id.prefix == "world":
            raise ValueError("Argument 'world_id' must be prefixed with 'world'")
        self._world_repository.retrieve(world_id)

    def _validate_no_linked_events_for_delete(self, location_id: PrefixedUUID) -> None:
        linked_event_ids = [str(event.id) for event in self._event_repository.retrieve_all(location_id=location_id)]
        if linked_event_ids:
            raise ValueError(f"Cannot delete location, currently linked to the following Events {','.join(linked_event_ids)}")

    def _validate_linked_events_still_intersect_for_update(self, updated_location: Location) -> None:
        linked_events = self._event_repository.retrieve_all(location_id=updated_location.id)
        for linked_event in linked_events:
            if not linked_event.span.intersects(updated_location.span):
                raise ValueError(f"Cannot modify location, currently linked to Event {linked_event.id} and the modification would "
                                 f"cause them to no longer intersect")
