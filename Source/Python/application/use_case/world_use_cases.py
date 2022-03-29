from logging import error
from typing import Set

from application.access.authentication import requires_authentication
from domain.ids import generate_prefixed_id, PrefixedUUID
from domain.worlds import World


class WorldUseCase:
    @requires_authentication()
    def create(self, **kwargs) -> World:
        kwargs["id"] = generate_prefixed_id("world")
        location = World(**kwargs)

        error(f"{self.create.__name__} method does not currently save the created world")

        return location

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
