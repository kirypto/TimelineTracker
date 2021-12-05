from typing import Set
from uuid import uuid4

from application.access.authentication import requires_authentication
from application.use_case.filtering_use_cases import FilteringUseCase
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.persistence.repositories import EventRepository, TravelerRepository, LocationRepository


class EventUseCase:
    _location_repository: LocationRepository
    _traveler_repository: TravelerRepository
    _event_repository: EventRepository

    def __init__(self, location_repository: LocationRepository, traveler_repository: TravelerRepository,  event_repository: EventRepository) -> None:
        if not isinstance(location_repository, LocationRepository):
            raise TypeError(f"Argument 'location_repository' must be of type {LocationRepository}")
        if not isinstance(traveler_repository, TravelerRepository):
            raise TypeError(f"Argument 'traveler_repository' must be of type {TravelerRepository}")
        if not isinstance(event_repository, EventRepository):
            raise TypeError(f"Argument 'event_repository' must be of type {EventRepository}")

        self._location_repository = location_repository
        self._traveler_repository = traveler_repository
        self._event_repository = event_repository

    @requires_authentication()
    def create(self, **kwargs) -> Event:
        kwargs["id"] = PrefixedUUID("event", uuid4())
        event = Event(**kwargs)

        self._validate_affected_entities(event)

        self._event_repository.save(event)

        return event

    @requires_authentication()
    def retrieve(self, event_id: PrefixedUUID) -> Event:
        if not event_id.prefix == "event":
            raise ValueError("Argument 'event_id' must be prefixed with 'event'")

        return self._event_repository.retrieve(event_id)

    @requires_authentication()
    def retrieve_all(self, **kwargs) -> Set[Event]:
        all_events = self._event_repository.retrieve_all()
        name_filtered_events, kwargs = FilteringUseCase.filter_named_entities(all_events, **kwargs)
        tag_filtered_events, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_events, **kwargs)
        span_filtered_events, kwargs = FilteringUseCase.filter_spanning_entities(tag_filtered_events, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return span_filtered_events

    @requires_authentication()
    def update(self, event: Event) -> None:
        self._event_repository.retrieve(event.id)

        self._validate_affected_entities(event)

        self._event_repository.save(event)

    @requires_authentication()
    def delete(self, event_id: PrefixedUUID) -> None:
        if not event_id.prefix == "event":
            raise ValueError("Argument 'event_id' must be prefixed with 'event'")

        return self._event_repository.delete(event_id)

    def _validate_affected_entities(self, updated_event: Event) -> None:
        for affected_location_id in updated_event.affected_locations:
            location = self._location_repository.retrieve(affected_location_id)
            if not location.span.intersects(updated_event.span):
                raise ValueError(f"Event's span does not intersect with {affected_location_id}'s span")

        for affected_traveler_id in updated_event.affected_travelers:
            traveler = self._traveler_repository.retrieve(affected_traveler_id)
            if not any([updated_event.span.includes(positional_move.position) for positional_move in traveler.journey]):
                raise ValueError(f"Event's span does not intersect with {affected_traveler_id}'s journey")
