from copy import deepcopy
from json import dumps
from pathlib import Path
from typing import Set, Dict

from adapter.request_handling.views import LocationView
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository


class InMemoryLocationRepository(LocationRepository):
    _locations_by_id: Dict[PrefixedUUID, Location]

    def __init__(self) -> None:
        self._locations_by_id = {}

    def save(self, location: Location) -> None:
        if not isinstance(location, Location):
            raise TypeError(f"Argument 'location' must be of type {Location}")

        self._locations_by_id[location.id] = location

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        if not isinstance(location_id, PrefixedUUID):
            raise TypeError(f"Argument 'location_id' must be of type {PrefixedUUID}")
        if location_id not in self._locations_by_id:
            raise NameError(f"No stored location with id '{location_id}'")

        return deepcopy(self._locations_by_id[location_id])

    def retrieve_all(self) -> Set[Location]:
        return {
            deepcopy(location)
            for location in self._locations_by_id.values()
        }

    def delete(self, location_id: PrefixedUUID) -> None:
        if location_id not in self._locations_by_id:
            raise NameError(f"No stored location with id '{location_id}'")

        self._locations_by_id.pop(location_id)


class JsonFileLocationRepository(LocationRepository):
    _location_repo_path: Path

    def __init__(self, *, json_repositories_directory_root: str) -> None:
        path = Path(json_repositories_directory_root)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"The path '{path}' is not a valid directory and cannot be used.")
        location_repo_path = path.joinpath("LocationRepo")
        if not location_repo_path.exists():
            location_repo_path.mkdir()
        if not location_repo_path.is_dir():
            raise ValueError(f"The path '{location_repo_path}' is not a valid directory and cannot be used.")
        self._location_repo_path = location_repo_path

    def save(self, location: Location) -> None:
        if not isinstance(location, Location):
            raise TypeError(f"Argument 'location' must be of type {Location.__name__}")

        location_file = self._location_repo_path.joinpath(f"{location.id}")
        if location_file.exists() and not location_file.is_file():
            raise FileExistsError(f"Could not save location {location.id}, an uncontrolled file already existed with the same name and path.")

        json = LocationView.to_json(location)
        location_file.write_text(dumps(json, indent=4), "utf8")

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        raise NotImplementedError("Not yet implemented")

    def retrieve_all(self) -> Set[Location]:
        raise NotImplementedError("Not yet implemented")

    def delete(self, location_id: PrefixedUUID) -> None:
        raise NotImplementedError("Not yet implemented")
