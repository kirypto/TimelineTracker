from typing import Set

from application.access.authentication import requires_authentication
from domain.ids import generate_prefixed_id, PrefixedUUID
from domain.persistence.repositories import WorldRepository
from domain.worlds import World


class WorldUseCase:
    _world_repository: WorldRepository

    def __init__(self, world_repository: WorldRepository) -> None:
        self._world_repository = world_repository

    @requires_authentication()
    def create(self, **kwargs) -> World:
        kwargs["id"] = generate_prefixed_id("world")
        world = World(**kwargs)

        self._world_repository.save(world)

        return world

    @requires_authentication()
    def retrieve(self, world_id: PrefixedUUID) -> World:
        raise NotImplementedError(f"{self.retrieve} has not been implemented")

    @requires_authentication()
    def retrieve_all(self, **kwargs) -> Set[World]:
        raise NotImplementedError(f"{self.retrieve_all} has not been implemented")

    @requires_authentication()
    def update(self, world: World) -> None:
        raise NotImplementedError(f"{self.update} has not been implemented")

    @requires_authentication()
    def delete(self, world_id: PrefixedUUID) -> None:
        raise NotImplementedError(f"{self.delete} has not been implemented")
