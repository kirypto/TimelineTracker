from typing import Set

from application.access.authentication import requires_authentication
from application.use_case.filtering_use_cases import FilteringUseCase
from domain.events import Event
from domain.ids import PrefixedUUID, generate_prefixed_id
from domain.persistence.repositories import EventRepository, TravelerRepository, LocationRepository, WorldRepository


class EventUseCase:
    _world_repository: WorldRepository
    _location_repository: LocationRepository
    _traveler_repository: TravelerRepository
    _event_repository: EventRepository

    def __init__(
            self, world_repository: WorldRepository, location_repository: LocationRepository, traveler_repository: TravelerRepository,
            event_repository: EventRepository) -> None:
        self._world_repository = world_repository
        self._location_repository = location_repository
        self._traveler_repository = traveler_repository
        self._event_repository = event_repository

    @requires_authentication()
    def create(self, world_id: PrefixedUUID, **kwargs) -> Event:
        self._validate_world_exists(world_id)
        kwargs["id"] = generate_prefixed_id("event")

        event = Event(**kwargs)
        self._validate_affected_entities(event)
        self._event_repository.save(event)
        self._world_repository.associate(world_id, event_id=event.id)

        return event

    @requires_authentication()
    def retrieve(self, world_id: PrefixedUUID, event_id: PrefixedUUID) -> Event:
        self._validate_world_exists(world_id)
        if not event_id.prefix == "event":
            raise ValueError("Argument 'event_id' must be prefixed with 'event'")
        associated_events = self._world_repository.get_all_associated(world_id, events=True)
        if event_id not in associated_events:
            raise NameError(f"No event '{event_id}' is exists for world '{world_id}'")

        return self._event_repository.retrieve(event_id)

    @requires_authentication()
    def retrieve_all(self, world_id: PrefixedUUID, **kwargs) -> Set[Event]:
        self._validate_world_exists(world_id)
        associated_events = self._world_repository.get_all_associated(world_id, events=True)
        all_events = {event for event in self._event_repository.retrieve_all() if event.id in associated_events}
        name_filtered_events, kwargs = FilteringUseCase.filter_named_entities(all_events, **kwargs)
        tag_filtered_events, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_events, **kwargs)
        span_filtered_events, kwargs = FilteringUseCase.filter_spanning_entities(tag_filtered_events, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return span_filtered_events

    @requires_authentication()
    def update(self, world_id: PrefixedUUID, event: Event) -> None:
        self._validate_world_exists(world_id)
        associated_events = self._world_repository.get_all_associated(world_id, events=True)
        if event.id not in associated_events:
            raise NameError(f"No event '{event.id}' is exists for world '{world_id}'")

        self._event_repository.retrieve(event.id)
        self._validate_affected_entities(event)

        self._event_repository.save(event)

    @requires_authentication()
    def delete(self, world_id: PrefixedUUID, event_id: PrefixedUUID) -> None:
        self._validate_world_exists(world_id)
        if not event_id.prefix == "event":
            raise ValueError("Argument 'event_id' must be prefixed with 'event'")
        associated_events = self._world_repository.get_all_associated(world_id, events=True)
        if event_id not in associated_events:
            raise NameError(f"No event '{event_id}' is exists for world '{world_id}'")

        return self._event_repository.delete(event_id)

    def _validate_world_exists(self, world_id: PrefixedUUID) -> None:
        if not world_id.prefix == "world":
            raise ValueError("Argument 'world_id' must be prefixed with 'world'")
        self._world_repository.retrieve(world_id)

    def _validate_affected_entities(self, event: Event) -> None:
        for affected_location_id in event.affected_locations:
            location = self._location_repository.retrieve(affected_location_id)
            if not location.span.intersects(event.span):
                raise ValueError(f"Event's span does not intersect with {affected_location_id}'s span")

        for affected_traveler_id in event.affected_travelers:
            traveler = self._traveler_repository.retrieve(affected_traveler_id)
            if not any([event.span.includes(positional_move.position) for positional_move in traveler.journey]):
                raise ValueError(f"Event's span does not intersect with {affected_traveler_id}'s journey")
