from typing import Set

from application.access.authentication import requires_authentication
from application.use_case.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID, generate_prefixed_id
from domain.persistence.repositories import TravelerRepository, EventRepository
from domain.travelers import Traveler


class TravelerUseCase:
    _event_repository: EventRepository
    _traveler_repository: TravelerRepository

    def __init__(self, traveler_repository: TravelerRepository, event_repository: EventRepository) -> None:
        if not isinstance(traveler_repository, TravelerRepository):
            raise TypeError(f"Argument 'traveler_repository' must be of type {TravelerRepository}")
        if not isinstance(event_repository, EventRepository):
            raise TypeError(f"Argument 'event_repository' must be of type {EventRepository}")

        self._event_repository = event_repository
        self._traveler_repository = traveler_repository

    @requires_authentication()
    def create(self, world_id: PrefixedUUID, **kwargs) -> Traveler:
        kwargs["id"] = generate_prefixed_id("traveler")

        traveler = Traveler(**kwargs)
        self._traveler_repository.save(world_id, traveler)
        return traveler

    @requires_authentication()
    def retrieve(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> Traveler:
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")

        return self._traveler_repository.retrieve(world_id, traveler_id)

    @requires_authentication()
    def retrieve_all(self, world_id: PrefixedUUID, **kwargs) -> Set[Traveler]:
        all_travelers = self._traveler_repository.retrieve_all(world_id)
        name_filtered_travelers, kwargs = FilteringUseCase.filter_named_entities(all_travelers, **kwargs)
        tag_filtered_travelers, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_travelers, **kwargs)
        journey_filtered_travelers, kwargs = FilteringUseCase.filter_journeying_entities(tag_filtered_travelers, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return journey_filtered_travelers

    @requires_authentication()
    def update(self, world_id: PrefixedUUID, traveler: Traveler) -> None:
        self._traveler_repository.retrieve(world_id, traveler.id)
        self._validate_linked_events_still_intersect_for_update(world_id, traveler)

        self._traveler_repository.save(world_id, traveler)

    @requires_authentication()
    def delete(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> None:
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")

        self._validate_no_linked_events_for_delete(world_id, traveler_id)

        self._traveler_repository.delete(world_id, traveler_id)

    def _validate_no_linked_events_for_delete(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> None:
        linked_event_ids = [str(event.id) for event in self._event_repository.retrieve_all(world_id, traveler_id=traveler_id)]
        if linked_event_ids:
            raise ValueError(f"Cannot delete traveler, currently linked to the following Events {','.join(linked_event_ids)}")

    def _validate_linked_events_still_intersect_for_update(self, world_id: PrefixedUUID, updated_traveler: Traveler) -> None:
        linked_events = self._event_repository.retrieve_all(world_id, traveler_id=updated_traveler.id)
        for linked_event in linked_events:
            if not any([linked_event.span.includes(move.position) for move in updated_traveler.journey]):
                raise ValueError(f"Cannot modify traveler, currently linked to Event {linked_event.id} and the modification would cause "
                                 f"them to no longer intersect")
