from typing import Set
from uuid import uuid4

from application.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID
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

    def create(self, **kwargs) -> Traveler:
        kwargs["id"] = PrefixedUUID(prefix="traveler", uuid=uuid4())

        traveler = Traveler(**kwargs)
        self._traveler_repository.save(traveler)
        return traveler

    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")

        return self._traveler_repository.retrieve(traveler_id)

    def retrieve_all(self, **kwargs) -> Set[Traveler]:
        all_travelers = self._traveler_repository.retrieve_all()
        name_filtered_travelers, kwargs = FilteringUseCase.filter_named_entities(all_travelers, **kwargs)
        tag_filtered_travelers, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_travelers, **kwargs)
        journey_filtered_travelers, kwargs = FilteringUseCase.filter_journeying_entities(tag_filtered_travelers, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return journey_filtered_travelers

    def update(self, traveler_id: PrefixedUUID, **kwargs) -> Traveler:
        if "id" in kwargs:
            raise ValueError(f"Cannot update 'id' attribute of {Traveler.__name__}")
        existing_traveler = self._traveler_repository.retrieve(traveler_id)
        updated_traveler = Traveler(
            id=traveler_id,
            name=kwargs.pop("name") if "name" in kwargs else existing_traveler.name,
            description=kwargs.pop("description") if "description" in kwargs else existing_traveler.description,
            journey=kwargs.pop("journey") if "journey" in kwargs else existing_traveler.journey,
            tags=kwargs.pop("tags") if "tags" in kwargs else existing_traveler.tags,
            **kwargs
        )

        self._validate_linked_events_still_intersect_for_update(updated_traveler)

        self._traveler_repository.save(updated_traveler)
        return updated_traveler

    def delete(self, traveler_id: PrefixedUUID) -> None:
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")

        self._validate_no_linked_events_for_delete(traveler_id)

        self._traveler_repository.delete(traveler_id)

    def _validate_no_linked_events_for_delete(self, traveler_id: PrefixedUUID) -> None:
        all_events = self._event_repository.retrieve_all()
        linked_event_ids = [str(event.id) for event in all_events if traveler_id in event.affected_travelers]
        if linked_event_ids:
            raise ValueError(f"Cannot delete traveler, currently linked to the following Events {','.join(linked_event_ids)}")

    def _validate_linked_events_still_intersect_for_update(self, updated_traveler: Traveler) -> None:
        all_events = self._event_repository.retrieve_all()
        linked_events = [event for event in all_events if updated_traveler.id in event.affected_travelers]
        for linked_event in linked_events:
            if not any([linked_event.span.includes(move.position) for move in updated_traveler.journey]):
                raise ValueError(f"Cannot modify traveler, currently linked to Event {linked_event.id} and the modification would cause them to no "
                                 f"longer intersect")
