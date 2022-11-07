from importlib import import_module
from typing import TypeVar, Type

from application.requests.rest.controllers import RESTController
from domain.persistence.repositories import TravelerRepository, LocationRepository, EventRepository, WorldRepository


TClass = TypeVar("TClass")


def _load_class(class_path: str, class_type: Type[TClass], **class_kwargs) -> TClass:
    module_name, class_name = class_path.rsplit(".", maxsplit=1)
    module = import_module(module_name)
    object_class = getattr(module, class_name)

    loaded = object_class(**class_kwargs)
    if not isinstance(loaded, class_type):
        raise ValueError(f"{class_path} did not result in a {class_type} object.")

    return loaded


class RepositoriesFactory:
    _REPO_TYPES = {
        "memory": "in_memory_repositories",
        "json": "json_file_repositories",
    }
    _world_repo: WorldRepository
    _location_repo: LocationRepository
    _traveler_repo: TravelerRepository
    _event_repo: EventRepository

    @property
    def world_repo(self) -> WorldRepository:
        return self._world_repo

    @property
    def location_repo(self) -> LocationRepository:
        return self._location_repo

    @property
    def traveler_repo(self) -> TravelerRepository:
        return self._traveler_repo

    @property
    def event_repo(self) -> EventRepository:
        return self._event_repo

    def __init__(
            self, *, world_repo_class_path: str, location_repo_class_path: str, traveler_repo_class_path: str, event_repo_class_path: str,
            **kwargs
    ) -> None:
        self._world_repo = _load_class(world_repo_class_path, WorldRepository, **kwargs)
        self._location_repo = _load_class(location_repo_class_path, LocationRepository, **kwargs)
        self._traveler_repo = _load_class(traveler_repo_class_path, TravelerRepository, **kwargs)
        self._event_repo = _load_class(event_repo_class_path, EventRepository, **kwargs)


class RESTControllersFactory:
    _rest_controller: RESTController

    @property
    def rest_controller(self) -> RESTController:
        return self._rest_controller

    def __init__(self, *, controller_class_path: str, **kwargs) -> None:
        module, class_name = controller_class_path.rsplit(".", maxsplit=1)
        controller_module = import_module(module)
        rest_controller_class = getattr(controller_module, class_name)

        rest_controller = rest_controller_class(**kwargs)
        if not isinstance(rest_controller, RESTController):
            raise ValueError(f"{controller_class_path} did not result in a {RESTController} object.")

        self._rest_controller = rest_controller
