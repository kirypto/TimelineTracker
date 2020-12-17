from typing import Set
from uuid import uuid4

from application.filtering_use_cases import FilteringUseCase
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

    def create(self, **kwargs) -> Event:
        kwargs["id"] = PrefixedUUID("event", uuid4())
        event = Event(**kwargs)

        self._validate_affected_entities(event)

        self._event_repository.save(event)

        return event

    def retrieve(self, event_id: PrefixedUUID) -> Event:
        if not event_id.prefix == "event":
            raise ValueError("Argument 'event_id' must be prefixed with 'event'")

        return self._event_repository.retrieve(event_id)

    def retrieve_all(self, **kwargs) -> Set[Event]:
        all_events = self._event_repository.retrieve_all()
        name_filtered_events, kwargs = FilteringUseCase.filter_named_entities(all_events, **kwargs)
        tag_filtered_events, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_events, **kwargs)
        span_filtered_events, kwargs = FilteringUseCase.filter_spanning_entities(tag_filtered_events, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return span_filtered_events

    def update(self, event_id: PrefixedUUID, **kwargs) -> Event:
        if "id" in kwargs:
            raise ValueError(f"Cannot update 'id' attribute of {Event.__name__}")
        existing_event = self._event_repository.retrieve(event_id)
        updated_event = Event(
            id=event_id, name=kwargs.pop("name") if "name" in kwargs else existing_event.name,
            description=kwargs.pop("description") if "description" in kwargs else existing_event.description,
            span=kwargs.pop("span") if "span" in kwargs else existing_event.span,
            tags=kwargs.pop("tags") if "tags" in kwargs else existing_event.tags,
            affected_locations=kwargs.pop("affected_locations") if "affected_locations" in kwargs else existing_event.affected_locations,
            affected_travelers=kwargs.pop("affected_travelers") if "affected_travelers" in kwargs else existing_event.affected_travelers,
            **kwargs)

        self._validate_affected_entities(updated_event)

        self._event_repository.save(updated_event)
        return updated_event

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
