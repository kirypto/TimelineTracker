from uuid import uuid4

from domain.ids import PrefixedUUID
from domain.persistence.repositories import TravelerRepository
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

