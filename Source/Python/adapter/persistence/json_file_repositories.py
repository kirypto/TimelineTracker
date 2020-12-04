from json import dumps, loads
from pathlib import Path
from typing import Set, Type, Generic, TypeVar

from adapter.views import LocationView, TravelerView, DomainConstructedView
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository
from domain.travelers import Traveler


_T = TypeVar('_T', bound=IdentifiedEntity)


class _JsonFileIdentifiedEntityRepository(Generic[_T]):
    _repo_path: Path
    _entity_type: Type[_T]
    _entity_view_type: Type[DomainConstructedView]

    @property
    def repo_path(self) -> Path:
        return self._repo_path

    def __init__(self, repo_name: str, entity_type: Type[_T], entity_view_type: Type[DomainConstructedView], *,
                 json_repositories_directory_root: str) -> None:
        root_repos_path = Path(json_repositories_directory_root)
        if not root_repos_path.exists() or not root_repos_path.is_dir():
            raise ValueError(f"The path '{root_repos_path}' is not a valid directory and cannot be used.")
        repo_path = root_repos_path.joinpath(repo_name)
        if not repo_path.exists():
            repo_path.mkdir()
        if not repo_path.is_dir():
            raise ValueError(f"The path '{repo_path}' is not a valid directory and cannot be used.")
        self._repo_path = repo_path
        self._entity_type = entity_type
        self._entity_view_type = entity_view_type

    def save(self, entity: _T) -> None:
        if not isinstance(entity, self._entity_type):
            raise TypeError(f"Argument 'entity' must be of type {self._entity_type}")

        entity_path = self._repo_path.joinpath(f"{entity.id}.json")
        if entity_path.exists() and not entity_path.is_file():
            raise FileExistsError(f"Could not save location {entity.id}, an uncontrolled non-file entity exists with the same name and path.")

        json = self._entity_view_type.to_json(entity)
        entity_path.write_text(dumps(json, indent=2), "utf8")

    def retrieve(self, entity_id: PrefixedUUID) -> _T:
        if not isinstance(entity_id, PrefixedUUID):
            raise TypeError(f"Argument 'entity_id' must be of type {PrefixedUUID}")
        return self._retrieve_entity_from_json_file(str(entity_id))

    def retrieve_all(self) -> Set[_T]:
        existing_entity_id_strings = [file.name.replace(".json", "") for file in self._repo_path.iterdir() if file.is_file()]

        all_entities = set()
        for entity_id_str in existing_entity_id_strings:
            all_entities.add(self._retrieve_entity_from_json_file(entity_id_str))
        return all_entities

    def delete(self, entity_id: PrefixedUUID) -> None:
        if not isinstance(entity_id, PrefixedUUID):
            raise TypeError(f"Argument 'entity_id' must be of type {PrefixedUUID}")

        entity_path = self._repo_path.joinpath(f"{entity_id}.json")
        if not entity_path.exists():
            raise NameError(f"No stored entity with id {entity_id}")

        entity_path.unlink()

    def _retrieve_entity_from_json_file(self, entity_id_str: str) -> _T:
        entity_path = self._repo_path.joinpath(f"{entity_id_str}.json")
        if entity_path.exists() and not entity_path.is_file():
            raise FileExistsError(f"Could not retrieve entity {entity_id_str}, an uncontrolled non-file entity exists with the same name and path.")
        if not entity_path.exists():
            raise NameError(f"No stored entity with id {entity_id_str}")

        entity_json = loads(entity_path.read_text(encoding="utf8"))
        return self._entity_type(**self._entity_view_type.kwargs_from_json(entity_json))


class JsonFileLocationRepository(LocationRepository):
    _inner_repo: _JsonFileIdentifiedEntityRepository[Location]

    def __init__(self, **kwargs) -> None:
        self._inner_repo = _JsonFileIdentifiedEntityRepository("LocationRepo", Location, LocationView, **kwargs)

    def save(self, location: Location) -> None:
        self._inner_repo.save(location)

    def retrieve(self, location_id: PrefixedUUID) -> Location:
        return self._inner_repo.retrieve(location_id)

    def retrieve_all(self) -> Set[Location]:
        return self._inner_repo.retrieve_all()

    def delete(self, location_id: PrefixedUUID) -> None:
        self._inner_repo.delete(location_id)


class JsonFileTravelerRepository(TravelerRepository):
    _inner_repo: _JsonFileIdentifiedEntityRepository[Traveler]

    def __init__(self, **kwargs) -> None:
        self._inner_repo = _JsonFileIdentifiedEntityRepository("TravelerRepo", Traveler, TravelerView, **kwargs)

    def save(self, traveler: Traveler) -> None:
        self._inner_repo.save(traveler)

    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        return self._inner_repo.retrieve(traveler_id)

    def retrieve_all(self) -> Set[Traveler]:
        return self._inner_repo.retrieve_all()

    def delete(self, traveler_id: PrefixedUUID) -> None:
        self._inner_repo.delete(traveler_id)
