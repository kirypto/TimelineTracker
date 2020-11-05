from uuid import uuid4

from domain.ids import PrefixedUUID
from domain.locations import Location


class LocationUseCase:
    def create(self, **kwargs) -> Location:
        location_id = PrefixedUUID("location", uuid4())
        print(f"Created location {location_id}")
        kwargs["id"] = location_id

        return Location(**kwargs)
