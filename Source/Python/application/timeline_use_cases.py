from typing import List, Union, Set

from application.filtering_use_cases import FilteringUseCase
from domain.collections import Range
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.persistence.repositories import LocationRepository, EventRepository, TravelerRepository
from domain.positions import MovementType, PositionalMove


class TimelineUseCase:
    _location_repository: LocationRepository
    _traveler_repository: TravelerRepository
    _event_repository: EventRepository

    def __init__(self, location_repository: LocationRepository, traveler_repository: TravelerRepository, event_repository: EventRepository) -> None:
        self._location_repository = location_repository
        self._traveler_repository = traveler_repository
        self._event_repository = event_repository

    def construct_location_timeline(self, location_id: PrefixedUUID, **filter_kwargs) -> List[PrefixedUUID]:
        def get_continuum(e: Event) -> Range:
            return e.span.continuum

        self._location_repository.retrieve(location_id)
        events = self._event_repository.retrieve_all(location_id=location_id)

        events, filter_kwargs = FilteringUseCase.filter_tagged_entities(events, **filter_kwargs)
        if filter_kwargs:
            raise ValueError(f"Unknown filters: {','.join(filter_kwargs)}")

        events_ordered_by_continuum = sorted(events, key=get_continuum)
        return [event.id for event in events_ordered_by_continuum]

    def construct_traveler_timeline(self, traveler_id: PrefixedUUID, **filter_kwargs) -> List[Union[PrefixedUUID, PositionalMove]]:
        traveler = self._traveler_repository.retrieve(traveler_id)
        events = self._event_repository.retrieve_all(traveler_id=traveler_id)

        events, filter_kwargs = FilteringUseCase.filter_tagged_entities(events, **filter_kwargs)
        if filter_kwargs:
            raise ValueError(f"Unknown filters: {','.join(filter_kwargs)}")

        already_applicable_events: Set[Event] = set([])
        timeline: List[Union[PrefixedUUID, PositionalMove]] = []
        for curr_positional_move in traveler.journey:
            curr_position = curr_positional_move.position

            already_applicable_events = {event for event in already_applicable_events if event.span.includes(curr_position)}
            newly_applicable_events: Set[Event] = {
                event for event in events
                if event.span.includes(curr_position) and event not in already_applicable_events
            }
            already_applicable_events.update(newly_applicable_events)

            if curr_positional_move.movement_type == MovementType.IMMEDIATE:
                timeline.append(curr_positional_move)
                timeline.extend(map(lambda event: event.id, newly_applicable_events))
            else:
                timeline.extend(map(lambda event: event.id, newly_applicable_events))
                timeline.append(curr_positional_move)

        return timeline


