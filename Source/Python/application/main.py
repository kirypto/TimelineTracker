from pathlib import Path
from typing import NoReturn, Dict, Any

from _version import __version__
from application.factories import RepositoriesFactory, RequestHandlersFactory
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from domain.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler, EventsRequestHandler


_INITIALIZATION_DATA: Dict[str, Any] = {
    "isAccessible": False,
}


class AppInitializationData(object):
    _instance = None

    def __new__(cls) -> NoReturn:
        raise AttributeError(f"{AppInitializationData.__name__} cannot be instantiated")

    @staticmethod
    def get_version() -> str:
        AppInitializationData.__validate_data_accessible()
        return _INITIALIZATION_DATA["version"]

    @staticmethod
    def get_resources_folder() -> Path:
        AppInitializationData.__validate_data_accessible()
        return _INITIALIZATION_DATA["resources_folder"]

    @staticmethod
    def __validate_data_accessible():
        if not _INITIALIZATION_DATA["isAccessible"]:
            raise ValueError(f"Cannot access {AppInitializationData} outside of application boot up period")


class TimelineTrackerApp:
    _version: str
    _resources_folder: Path
    _locations_request_handler: LocationsRequestHandler
    _travelers_request_handler: TravelersRequestHandler
    _event_request_handler: EventsRequestHandler

    @property
    def version(self) -> str:
        return __version__

    @property
    def resources_folder(self) -> Path:
        return self._resources_folder

    @property
    def locations_request_handler(self) -> LocationsRequestHandler:
        return self._locations_request_handler

    @property
    def travelers_request_handler(self) -> TravelersRequestHandler:
        return self._travelers_request_handler

    @property
    def event_request_handler(self) -> EventsRequestHandler:
        return self._event_request_handler

    def __init__(self, *, resources_folder_path: str, repositories_config: dict, request_handlers_config: dict) -> None:
        self._resources_folder = Path(resources_folder_path).resolve()
        if not self._resources_folder.exists() or not self._resources_folder.is_dir():
            raise ValueError(f"The provided resources folder does not exist or was not a directory. Was '{self._resources_folder}'.")
        _INITIALIZATION_DATA["version"] = __version__
        _INITIALIZATION_DATA["resources_folder"] = self.resources_folder
        _INITIALIZATION_DATA["isAccessible"] = True

        repositories_factory = RepositoriesFactory(**repositories_config)
        location_repository = repositories_factory.location_repo
        traveler_repository = repositories_factory.traveler_repo
        event_repository = repositories_factory.event_repo

        location_use_case = LocationUseCase(location_repository, event_repository)
        traveler_use_case = TravelerUseCase(traveler_repository, event_repository)
        event_use_case = EventUseCase(location_repository, traveler_repository, event_repository)
        timeline_use_case = TimelineUseCase(location_repository, traveler_repository, event_repository)

        request_handlers_factory = RequestHandlersFactory(
            location_use_case, traveler_use_case, event_use_case, timeline_use_case, **request_handlers_config)
        self._locations_request_handler = request_handlers_factory.location_handler
        self._travelers_request_handler = request_handlers_factory.traveler_handler
        self._event_request_handler = request_handlers_factory.event_handler

        _INITIALIZATION_DATA["isAccessible"] = False
