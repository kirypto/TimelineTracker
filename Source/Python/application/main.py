from pathlib import Path

from _version import __version__
from application.factories import RepositoriesFactory, RESTControllersFactory
from application.requests.rest.handlers import LocationsRestRequestHandler, TravelersRestRequestHandler, EventsRestRequestHandler
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from util.logging import configure_logging


class TimelineTrackerApp:
    _version: str
    _resources_folder: Path
    _locations_request_handler: LocationsRestRequestHandler
    _travelers_request_handler: TravelersRestRequestHandler
    _event_request_handler: EventsRestRequestHandler

    _location_use_case: LocationUseCase
    _traveler_use_case: TravelerUseCase
    _event_use_case: EventUseCase
    _timeline_use_case: TimelineUseCase

    @property
    def version(self) -> str:
        return __version__

    @property
    def resources_folder(self) -> Path:
        return self._resources_folder

    @property
    def locations_request_handler(self) -> LocationsRestRequestHandler:
        return self._locations_request_handler

    @property
    def travelers_request_handler(self) -> TravelersRestRequestHandler:
        return self._travelers_request_handler

    @property
    def event_request_handler(self) -> EventsRestRequestHandler:
        return self._event_request_handler

    def __init__(self, *, resources_folder_path: str, repositories_config: dict, logging_config: dict = None) -> None:
        configure_logging(**(logging_config if logging_config is not None else {}))

        self._resources_folder = Path(resources_folder_path).resolve()
        if not self._resources_folder.exists() or not self._resources_folder.is_dir():
            raise ValueError(f"The provided resources folder does not exist or was not a directory. Was '{self._resources_folder}'.")

        repositories_factory = RepositoriesFactory(**repositories_config)
        location_repository = repositories_factory.location_repo
        traveler_repository = repositories_factory.traveler_repo
        event_repository = repositories_factory.event_repo

        self._location_use_case = LocationUseCase(location_repository, event_repository)
        self._traveler_use_case = TravelerUseCase(traveler_repository, event_repository)
        self._event_use_case = EventUseCase(location_repository, traveler_repository, event_repository)
        self._timeline_use_case = TimelineUseCase(location_repository, traveler_repository, event_repository)

    def initialize_controllers(self, *, rest_controller_config: dict) -> None:
        rest_controller = RESTControllersFactory(**rest_controller_config).rest_controller

        LocationsRestRequestHandler.register_routes(rest_controller, self._location_use_case, self._timeline_use_case)
        TravelersRestRequestHandler.register_routes(rest_controller, self._traveler_use_case, self._timeline_use_case)
        EventsRestRequestHandler.register_routes(rest_controller, self._event_use_case)

        rest_controller.finalize()
