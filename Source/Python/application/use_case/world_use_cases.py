from typing import Set

from application.access.authentication import requires_authentication
from application.use_case.filtering_use_cases import FilteringUseCase
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
        if not world_id.prefix == "world":
            raise ValueError("Argument 'world_id' must be prefixed with 'world'")

        return self._world_repository.retrieve(world_id)

    @requires_authentication()
    def retrieve_all(self, **kwargs) -> Set[World]:
        all_worlds = self._world_repository.retrieve_all()
        name_filtered_worlds, kwargs = FilteringUseCase.filter_named_entities(all_worlds, **kwargs)
        tag_filtered_worlds, kwargs = FilteringUseCase.filter_tagged_entities(name_filtered_worlds, **kwargs)
        if kwargs:
            raise ValueError(f"Unknown filters: {','.join(kwargs)}")

        return tag_filtered_worlds

    @requires_authentication()
    def update(self, world: World) -> None:
        self._world_repository.retrieve(world.id)
        self._world_repository.save(world)

    @requires_authentication()
    def delete(self, world_id: PrefixedUUID) -> None:
        if not world_id.prefix == "world":
            raise ValueError("Argument 'world_id' must be prefixed with 'world'")

        self._world_repository.delete(world_id)
