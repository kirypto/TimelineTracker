from typing import Set, List
from uuid import uuid4

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
        return self._traveler_repository.retrieve(traveler_id)

    def retrieve_all(self, *, name: str = None, tagged_with_all: Set[Tag] = None, tagged_with_any: Set[Tag] = None, tagged_with_only: Set[Tag] = None,
                     tagged_with_none: Set[Tag] = None) -> Set[Traveler]:
        def matches_filters(traveler: Traveler) -> bool:
            if name is not None and traveler.name != name:
                return False
            if tagged_with_all is not None and not tagged_with_all.issubset(traveler.tags):
                return False
            if tagged_with_any is not None and not tagged_with_any.intersection(traveler.tags):
                return False
            if tagged_with_only is not None and not tagged_with_only.issuperset(traveler.tags):
                return False
            if tagged_with_none is not None and not tagged_with_none.isdisjoint(traveler.tags):
                return False
            return True

        return {traveler for traveler in self._traveler_repository.retrieve_all() if matches_filters(traveler)}

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

