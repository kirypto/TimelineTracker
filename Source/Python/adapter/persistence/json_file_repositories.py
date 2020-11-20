from json import dumps, loads
from pathlib import Path
from typing import Set

from adapter.views import LocationView, TravelerView
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository
from domain.travelers import Traveler


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
            raise TypeError(f"Argument 'location' must be of type {Location}")

        location_file = self._location_repo_path.joinpath(f"{location.id}.json")
        if location_file.exists() and not location_file.is_file():
            raise FileExistsError(f"Could not save location {location.id}, an uncontrolled non-file entity exists with the same name and path.")

        json = LocationView.to_json(location)
        location_file.write_text(dumps(json, indent=4), "utf8")

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        if not isinstance(location_id, PrefixedUUID):
            raise TypeError(f"Argument 'location_id' must be of type {PrefixedUUID}")
        return self._retrieve_location_from_json_file(str(location_id))

    def retrieve_all(self) -> Set[Location]:
        existing_location_id_strings = [file.name.replace(".json", "") for file in self._location_repo_path.iterdir() if file.is_file()]

        return {self._retrieve_location_from_json_file(location_id_str) for location_id_str in existing_location_id_strings}

    def delete(self, location_id: PrefixedUUID) -> None:
        if not isinstance(location_id, PrefixedUUID):
            raise TypeError(f"Argument 'location_id' must be of type {PrefixedUUID}")

        location_file = self._location_repo_path.joinpath(f"{location_id}.json")
        if not location_file.exists():
            raise NameError(f"No stored location with id {location_id}")

        location_file.unlink()

    def _retrieve_location_from_json_file(self, location_id_str: str) -> Location:
        location_file = self._location_repo_path.joinpath(f"{location_id_str}.json")
        if location_file.exists() and not location_file.is_file():
            raise FileExistsError(f"Could not retrieve location {location_id_str}, an uncontrolled non-file entity exists with the same name and "
                                  f"path.")
        if not location_file.exists():
            raise NameError(f"No stored location with id {location_id_str}")

        location_json = loads(location_file.read_text(encoding="utf8"))
        return Location(**LocationView.kwargs_from_json(location_json))


class JsonFileTravelerRepository(TravelerRepository):
    _traveler_repo_path: Path

    def __init__(self, *, json_repositories_directory_root: str) -> None:
        path = Path(json_repositories_directory_root)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"The path '{path}' is not a valid directory and cannot be used.")
        traveler_repo_path = path.joinpath("TravelerRepo")
        if not traveler_repo_path.exists():
            traveler_repo_path.mkdir()
        if not traveler_repo_path.is_dir():
            raise ValueError(f"The path '{traveler_repo_path}' is not a valid directory and cannot be used.")
        self._traveler_repo_path = traveler_repo_path

    def save(self, traveler: Traveler) -> None:
        if not isinstance(traveler, Traveler):
            raise TypeError(f"Argument 'traveler' must be of type {Traveler}")

        traveler_file = self._traveler_repo_path.joinpath(f"{traveler.id}.json")
        if traveler_file.exists() and not traveler_file.is_file():
            raise FileExistsError(f"Could not save traveler {traveler.id}, an uncontrolled non-file entity exists with the same name and path.")

        json = TravelerView.to_json(traveler)
        traveler_file.write_text(dumps(json, indent=4), "utf8")

    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        if not isinstance(traveler_id, PrefixedUUID):
            raise TypeError(f"Argument 'traveler_id' must be of type {PrefixedUUID}")
        return self._retrieve_traveler_from_json_file(str(traveler_id))

    def retrieve_all(self) -> Set[Traveler]:
        existing_traveler_id_strings = [file.name.replace(".json", "") for file in self._traveler_repo_path.iterdir() if file.is_file()]

        return {self._retrieve_traveler_from_json_file(traveler_id_str) for traveler_id_str in existing_traveler_id_strings}

    def delete(self, traveler_id: PrefixedUUID) -> None:
        if not isinstance(traveler_id, PrefixedUUID):
            raise TypeError(f"Argument 'traveler_id' must be of type {PrefixedUUID}")

        traveler_file = self._traveler_repo_path.joinpath(f"{traveler_id}.json")
        if not traveler_file.exists():
            raise NameError(f"No stored traveler with id {traveler_id}")

        traveler_file.unlink()

    def _retrieve_traveler_from_json_file(self, traveler_id_str: str) -> Traveler:
        traveler_file = self._traveler_repo_path.joinpath(f"{traveler_id_str}.json")
        if traveler_file.exists() and not traveler_file.is_file():
            raise FileExistsError(f"Could not retrieve traveler {traveler_id_str}, an uncontrolled non-file entity exists with the same name and "
                                  f"path.")
        if not traveler_file.exists():
            raise NameError(f"No stored traveler with id {traveler_id_str}")

        traveler_json = loads(traveler_file.read_text(encoding="utf8"))
        return Traveler(**TravelerView.kwargs_from_json(traveler_json))
