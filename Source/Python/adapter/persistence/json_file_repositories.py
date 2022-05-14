from json import dumps, loads
from pathlib import Path
from typing import Set, Type, Generic, TypeVar, Dict, Optional, List

from application.requests.data_forms import JsonTranslator
from domain.events import Event
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository, WorldRepository
from domain.travelers import Traveler
from domain.worlds import World


_T = TypeVar('_T', bound=IdentifiedEntity)
_METADATA_VERSION_FILE = "repository_version.metadata"
_WORLD_REPO_DIR_NAME = "WorldRepo"
_LOCATION_REPO_DIR_NAME = "LocationRepo"
_TRAVELER_REPO_DIR_NAME = "TravelerRepo"
_EVENT_REPO_DIR_NAME = "EventRepo"
_TIndex = TypeVar('_TIndex')


class _JsonFileIdentifiedEntityRepository(Generic[_T]):
    _repo_path: Path
    _entity_type: Type[_T]

    def __init__(self, repo_name: str, entity_type: Type[_T], *, json_repositories_directory_root: str) -> None:
        root_repos_path = Path(json_repositories_directory_root)
        print(root_repos_path.as_posix())
        if not root_repos_path.exists() or not root_repos_path.is_dir():
            raise ValueError(f"The path '{root_repos_path}' is not a valid directory and cannot be used.")
        repo_path = root_repos_path.joinpath(repo_name)
        if not repo_path.exists():
            repo_path.mkdir()
        if not repo_path.is_dir():
            raise ValueError(f"The path '{repo_path}' is not a valid directory and cannot be used.")

        self._repo_path = repo_path
        self._entity_type = entity_type

    def save(self, entity: _T) -> None:
        if not isinstance(entity, self._entity_type):
            raise TypeError(f"Argument 'entity' must be of type {self._entity_type}")

        entity_path = self._repo_path.joinpath(f"{entity.id}.json")
        if entity_path.exists() and not entity_path.is_file():
            raise FileExistsError(f"Could not save location {entity.id}, an uncontrolled non-file entity exists with the same name and "
                                  f"path.")

        json = JsonTranslator.to_json(entity)
        entity_path.write_text(dumps(json, indent=2), "utf8")

    def retrieve(self, entity_id: PrefixedUUID) -> _T:
        if not isinstance(entity_id, PrefixedUUID):
            raise TypeError(f"Argument 'entity_id' must be of type {PrefixedUUID}")
        return self._retrieve_entity_from_json_file(str(entity_id))

    def retrieve_all(self) -> Set[_T]:
        existing_entity_id_strings = [
            file.name.replace(".json", "")
            for file in self._repo_path.iterdir()
            if file.is_file() and file.suffix == ".json"
        ]

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

        deleted_suffix_path = entity_path.with_suffix(f"{entity_path.suffix}.deleted")
        entity_path.rename(deleted_suffix_path)

    def save_index(self, name: str, index: str) -> None:
        index_path = self._repo_path.joinpath(f"{name}.index")
        if index_path.exists() and not index_path.is_file():
            raise FileExistsError(
                f"Could not save index {name}, an uncontrolled non-file object already exists at path '{index_path.as_posix()}'.")

        index_path.write_text(index, encoding="utf8")

    def retrieve_index(self, name: str) -> Optional[str]:
        index_path = self._repo_path.joinpath(f"{name}.index")
        if not index_path.exists():
            return None
        if not index_path.is_file():
            raise FileExistsError(
                f"Could not retrieve index {name}, an uncontrolled non-file object already exists at path '{index_path.as_posix()}'.")

        return index_path.read_text(encoding="utf8")

    def _retrieve_entity_from_json_file(self, entity_id_str: str) -> _T:
        entity_path = self._repo_path.joinpath(f"{entity_id_str}.json")
        if entity_path.exists() and not entity_path.is_file():
            raise FileExistsError(f"Could not retrieve entity {entity_id_str}, "
                                  f"an uncontrolled non-file entity exists with the same name and path.")
        if not entity_path.exists():
            raise NameError(f"No stored entity with id {entity_id_str}")

        entity_json = entity_path.read_text(encoding="utf8")
        return JsonTranslator.from_json_str(entity_json, self._entity_type)


class JsonFileWorldRepository(WorldRepository):
    _inner_repo: _JsonFileIdentifiedEntityRepository[World]

    def __init__(self, **kwargs) -> None:
        self._inner_repo = _JsonFileIdentifiedEntityRepository(_WORLD_REPO_DIR_NAME, World, **kwargs)

    def save(self, world: World) -> None:
        self._inner_repo.save(world)

    def retrieve(self, world_id: PrefixedUUID) -> World:
        return self._inner_repo.retrieve(world_id)

    def retrieve_all(self) -> Set[World]:
        return self._inner_repo.retrieve_all()

    def delete(self, world_id: PrefixedUUID) -> None:
        self._inner_repo.delete(world_id)

    def associate(
            self, world_id: PrefixedUUID,
            *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None, event_id: PrefixedUUID = None
    ) -> None:
        if location_id is not None:
            index_name = "associated_locations"
            val = str(location_id)
        elif traveler_id is not None:
            index_name = "associated_travelers"
            val = str(traveler_id)
        elif event_id is not None:
            index_name = "associated_events"
            val = str(event_id)
        else:
            raise ValueError("Must provide a location_id, a traveler_id, or a event_id.")
        index_str = self._inner_repo.retrieve_index(index_name)
        index: Dict[str, Set[str]] = {key: set(vals) for key, vals in loads(index_str).items()} if index_str is not None else {}
        index_key = str(world_id)
        if index_key in index:
            index[index_key].add(val)
        else:
            index[index_key] = {val}
        self._inner_repo.save_index(index_name, dumps({key: list(vals) for key, vals in index.items()}))

    def disassociate(
            self, world_id: PrefixedUUID,
            *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None, event_id: PrefixedUUID = None
    ) -> None:
        if location_id is not None:
            index_name = "associated_locations"
            val = str(location_id)
        elif traveler_id is not None:
            index_name = "associated_travelers"
            val = str(traveler_id)
        elif event_id is not None:
            index_name = "associated_events"
            val = str(event_id)
        else:
            raise ValueError("Must provide a location_id, a traveler_id, or a event_id.")
        index_str = self._inner_repo.retrieve_index(index_name)
        index: Dict[str, Set[str]] = {key: set(vals) for key, vals in loads(index_str).items()} if index_str is not None else {}
        index_key = str(world_id)
        if index_key in index:
            index[index_key].remove(val)
        else:
            index[index_key] = {val}
        self._inner_repo.save_index(index_name, dumps({key: list(vals) for key, vals in index.items()}))

    def get_all_associated(
            self, world_id: PrefixedUUID, *, locations: bool = False, travelers: bool = False, events: bool = False
    ) -> Set[PrefixedUUID]:
        if locations:
            index_name = "associated_locations"
        elif travelers:
            index_name = "associated_travelers"
        elif events:
            index_name = "associated_events"
        else:
            raise ValueError(f"Exactly 1 entity type must be requested, was: locations={locations}, travelers={travelers}, events={events}")
        index_str = self._inner_repo.retrieve_index(index_name)
        index: Dict[str, List[str]] = loads(index_str) if index_str is not None else {}
        return {JsonTranslator.from_json_str(entity_id, PrefixedUUID) for entity_id in index.get(str(world_id), [])}


class JsonFileLocationRepository(LocationRepository):
    _inner_repo: _JsonFileIdentifiedEntityRepository[Location]

    def __init__(self, **kwargs) -> None:
        self._inner_repo = _JsonFileIdentifiedEntityRepository(_LOCATION_REPO_DIR_NAME, Location, **kwargs)

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
        self._inner_repo = _JsonFileIdentifiedEntityRepository(_TRAVELER_REPO_DIR_NAME, Traveler, **kwargs)

    def save(self, traveler: Traveler) -> None:
        self._inner_repo.save(traveler)

    def retrieve(self, traveler_id: PrefixedUUID) -> Traveler:
        return self._inner_repo.retrieve(traveler_id)

    def retrieve_all(self) -> Set[Traveler]:
        return self._inner_repo.retrieve_all()

    def delete(self, traveler_id: PrefixedUUID) -> None:
        self._inner_repo.delete(traveler_id)


class JsonFileEventRepository(EventRepository):
    _inner_repo: _JsonFileIdentifiedEntityRepository[Event]

    def __init__(self, **kwargs) -> None:
        self._inner_repo = _JsonFileIdentifiedEntityRepository(_EVENT_REPO_DIR_NAME, Event, **kwargs)

    def save(self, event: Event) -> None:
        self._inner_repo.save(event)
        self._add_to_index("event_ids_by_location_id", event.affected_locations, event.id)
        self._add_to_index("event_ids_by_traveler_id", event.affected_travelers, event.id)

    def retrieve(self, event_id: PrefixedUUID) -> Event:
        return self._inner_repo.retrieve(event_id)

    def retrieve_all(self, *, location_id: PrefixedUUID = None, traveler_id: PrefixedUUID = None) -> Set[Event]:
        if location_id is None and traveler_id is None:
            # Neither filter provided, return all
            return self._inner_repo.retrieve_all()

        events_linked_to_provided_location_id = self._retrieve_from_index("event_ids_by_location_id", location_id)
        events_linked_to_provided_traveler_id = self._retrieve_from_index("event_ids_by_traveler_id", traveler_id)
        if location_id is not None and traveler_id is not None:
            # Both filters provided, return events linked to both
            desired_event_ids = events_linked_to_provided_location_id.intersection(events_linked_to_provided_traveler_id)
        else:
            # Only on filter provided, return events linked to that one (union with empty set)
            desired_event_ids = events_linked_to_provided_location_id.union(events_linked_to_provided_traveler_id)
        return {self.retrieve(event_id) for event_id in desired_event_ids}

    def delete(self, event_id: PrefixedUUID) -> None:
        self._inner_repo.delete(event_id)
        self._strip_value_from_index_entries("event_ids_by_location_id", event_id)
        self._strip_value_from_index_entries("event_ids_by_traveler_id", event_id)

    def _strip_value_from_index_entries(self, name: str, value: PrefixedUUID) -> None:
        index_str = self._inner_repo.retrieve_index(name)
        if index_str is None:
            return
        index: Dict[str, List[str]] = loads(index_str)
        for key in index:
            index[key] = list(set(index[key]) - {str(value)})
        self._inner_repo.save_index(name, dumps(index))

    def _retrieve_from_index(self, name: str, key: PrefixedUUID) -> Set[PrefixedUUID]:
        index_str = self._inner_repo.retrieve_index(name)
        if index_str is None:
            return set()
        index: Dict[str, List[str]] = loads(index_str)
        return JsonTranslator.from_json(index.get(str(key), []), Set[PrefixedUUID])

    def _add_to_index(self, name: str, keys: Set[PrefixedUUID], val: PrefixedUUID) -> None:
        index_str = self._inner_repo.retrieve_index(name)
        if index_str is None:
            index = {}
        else:
            index: Dict[str, List[str]] = loads(index_str)
        for key in map(str, keys):
            if key in index:
                index[key].append(str(val))
            else:
                index[key] = [str(val)]
        self._inner_repo.save_index(name, dumps(index))
