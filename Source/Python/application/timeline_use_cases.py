from typing import List

from domain.collections import Range
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.persistence.repositories import LocationRepository, EventRepository


class TimelineUseCase:
    _location_repository: LocationRepository
    _event_repository: EventRepository

    def __init__(self, location_repository: LocationRepository, event_repository: EventRepository) -> None:
        self._location_repository = location_repository
        self._event_repository = event_repository

    def construct_location_timeline(self, location_id: PrefixedUUID) -> List[PrefixedUUID]:
        self._location_repository.retrieve(location_id)

        events = self._event_repository.retrieve_all(location_id=location_id)

        def get_continuum(e: Event) -> Range:
            return e.span.continuum

        events_ordered_by_continuum = sorted(events, key=get_continuum)

        return [event.id for event in events_ordered_by_continuum]
