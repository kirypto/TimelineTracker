from typing import Set
from uuid import uuid4

from application.filtering_use_cases import FilteringUseCase
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.persistence.repositories import EventRepository


class EventUseCase:
    _event_repository: EventRepository

    def __init__(self, event_repository: EventRepository) -> None:
        if not isinstance(event_repository, EventRepository):
            raise TypeError(f"Argument 'event_repository' must be of type {EventRepository}")

        self._event_repository = event_repository

    def create(self, **kwargs) -> Event:
        kwargs["id"] = PrefixedUUID("event", uuid4())
        event = Event(**kwargs)

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
            id=event_id,
            name=kwargs.pop("name") if "name" in kwargs else existing_event.name,
            description=kwargs.pop("description") if "description" in kwargs else existing_event.description,
            span=kwargs.pop("span") if "span" in kwargs else existing_event.span,
            tags=kwargs.pop("tags") if "tags" in kwargs else existing_event.tags,
            **kwargs
        )
        self._event_repository.save(updated_event)
        return updated_event

    def delete(self, event_id: PrefixedUUID) -> None:
        if not event_id.prefix == "event":
            raise ValueError("Argument 'event_id' must be prefixed with 'event'")

        return self._event_repository.delete(event_id)
