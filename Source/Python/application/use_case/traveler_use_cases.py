from typing import Set

from application.access.authentication import requires_authentication
from application.use_case.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID, generate_prefixed_id
from domain.persistence.repositories import TravelerRepository, EventRepository, WorldRepository
from domain.travelers import Traveler


class TravelerUseCase:
    _world_repository: WorldRepository
    _event_repository: EventRepository
    _traveler_repository: TravelerRepository

    def __init__(
            self, world_repository: WorldRepository, traveler_repository: TravelerRepository, event_repository: EventRepository
    ) -> None:
        if not isinstance(traveler_repository, TravelerRepository):
            raise TypeError(f"Argument 'traveler_repository' must be of type {TravelerRepository}")
        if not isinstance(event_repository, EventRepository):
            raise TypeError(f"Argument 'event_repository' must be of type {EventRepository}")
        self._world_repository = world_repository
        self._event_repository = event_repository
        self._traveler_repository = traveler_repository

    @requires_authentication()
    def create(self, world_id: PrefixedUUID, **kwargs) -> Traveler:
        self._validate_world_exists(world_id)
        kwargs["id"] = generate_prefixed_id("traveler")

        traveler = Traveler(**kwargs)
        self._traveler_repository.save(traveler)
        self._world_repository.associate(world_id, traveler_id=traveler.id)

        return traveler

    @requires_authentication()
    def retrieve(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> Traveler:
        self._validate_world_exists(world_id)
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")
        associated_travelers = self._world_repository.get_all_associated(world_id, travelers=True)
        if traveler_id not in associated_travelers:
            raise NameError(f"No traveler '{traveler_id}' is exists for world '{world_id}'")

        return self._traveler_repository.retrieve(traveler_id)

    @requires_authentication()
    def retrieve_all(self, world_id: PrefixedUUID, **kwargs) -> Set[Traveler]:
        self._validate_world_exists(world_id)
        associated_travelers = self._world_repository.get_all_associated(world_id, travelers=True)
        all_travelers = {traveler for traveler in self._traveler_repository.retrieve_all() if traveler.id in associated_travelers}
        name_filtered_travelers, kwargs = FilteringUseCase.filter_named_entities(all_travelers, **kwargs)
        tag_filtered_travelers, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_travelers, **kwargs)
        journey_filtered_travelers, kwargs = FilteringUseCase.filter_journeying_entities(tag_filtered_travelers, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return journey_filtered_travelers

    @requires_authentication()
    def update(self, world_id: PrefixedUUID, traveler: Traveler) -> None:
        self._validate_world_exists(world_id)
        associated_travelers = self._world_repository.get_all_associated(world_id, travelers=True)
        if traveler.id not in associated_travelers:
            raise NameError(f"No traveler '{traveler.id}' is exists for world '{world_id}'")

        self._traveler_repository.retrieve(traveler.id)
        self._validate_linked_events_still_intersect_for_update(traveler)

        self._traveler_repository.save(traveler)

    @requires_authentication()
    def delete(self, world_id: PrefixedUUID, traveler_id: PrefixedUUID) -> None:
        self._validate_world_exists(world_id)
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")
        associated_travelers = self._world_repository.get_all_associated(world_id, travelers=True)
        if traveler_id not in associated_travelers:
            raise NameError(f"No traveler '{traveler_id}' is exists for world '{world_id}'")

        self._validate_no_linked_events_for_delete(traveler_id)

        self._traveler_repository.delete(traveler_id)

    def _validate_world_exists(self, world_id: PrefixedUUID) -> None:
        if not world_id.prefix == "world":
            raise ValueError("Argument 'world_id' must be prefixed with 'world'")
        self._world_repository.retrieve(world_id)

    def _validate_no_linked_events_for_delete(self, traveler_id: PrefixedUUID) -> None:
        linked_event_ids = [str(event.id) for event in self._event_repository.retrieve_all(traveler_id=traveler_id)]
        if linked_event_ids:
            raise ValueError(f"Cannot delete traveler, currently linked to the following Events {','.join(linked_event_ids)}")

    def _validate_linked_events_still_intersect_for_update(self, updated_traveler: Traveler) -> None:
        linked_events = self._event_repository.retrieve_all(traveler_id=updated_traveler.id)
        for linked_event in linked_events:
            if not any([linked_event.span.includes(move.position) for move in updated_traveler.journey]):
                raise ValueError(f"Cannot modify traveler, currently linked to Event {linked_event.id} and the modification would cause "
                                 f"them to no longer intersect")
