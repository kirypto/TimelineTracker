from logging import error

from application.access.authentication import requires_authentication
from domain.ids import generate_prefixed_id
from domain.worlds import World


class WorldUseCase:
    @requires_authentication()
    def create(self, **kwargs) -> World:
        kwargs["id"] = generate_prefixed_id("world")
        location = World(**kwargs)

        error(f"{self.create.__name__} method does not currently save the created world")

        return location
