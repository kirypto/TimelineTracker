from typing import Set, List
from uuid import uuid4

from application.filtering_use_cases import FilteringUseCase
from domain.ids import PrefixedUUID
from domain.persistence.repositories import TravelerRepository
from domain.positions import PositionalMove
from domain.tags import Tag
from domain.travelers import Traveler


class TravelerUseCase:
    _traveler_repository: TravelerRepository

    def __init__(self, traveler_repository: TravelerRepository) -> None:
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

    def update(self, traveler_id: PrefixedUUID, *,
               name: str = None, description: str = None, journey: List[PositionalMove] = None, tags: Set[Tag] = None) -> Traveler:

        existing_traveler = self._traveler_repository.retrieve(traveler_id)

        updated_traveler = Traveler(
            id=traveler_id,
            name=name if name is not None else existing_traveler.name,
            description=description if description is not None else existing_traveler.description,
            journey=journey if journey is not None else existing_traveler.journey,
            tags=tags if tags is not None else existing_traveler.tags,
        )
        self._traveler_repository.save(updated_traveler)
        return updated_traveler

    def delete(self, traveler_id: PrefixedUUID) -> None:
        if not traveler_id.prefix == "traveler":
            raise ValueError("Argument 'traveler_id' must be prefixed with 'traveler'")

        self._traveler_repository.delete(traveler_id)

