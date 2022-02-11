from importlib import import_module

from application.requests.rest.controllers import RESTController
from application.requests.rest.handlers import LocationsRestRequestHandler, TravelersRestRequestHandler, EventsRestRequestHandler
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from domain.persistence.repositories import TravelerRepository, LocationRepository, EventRepository


class RepositoriesFactory:
    _REPO_TYPES = {
        "memory": "in_memory_repositories",
        "json": "json_file_repositories",
    }
    _location_repo: LocationRepository
    _traveler_repo: TravelerRepository
    _event_repo: EventRepository

    @property
    def location_repo(self) -> LocationRepository:
        return self._location_repo

    @property
    def traveler_repo(self) -> TravelerRepository:
        return self._traveler_repo

    @property
    def event_repo(self) -> EventRepository:
        return self._event_repo

    def __init__(self, repository_type: str, **kwargs) -> None:
        if repository_type not in RepositoriesFactory._REPO_TYPES:
            raise ValueError(f"Unsupported repository type {repository_type}. "
                             f"Supported types are: {set(RepositoriesFactory._REPO_TYPES.keys())}")

        repositories_module = import_module(f"adapter.persistence.{RepositoriesFactory._REPO_TYPES[repository_type]}")
        location_repository_class = getattr(repositories_module, "location_repository_class")
        traveler_repository_class = getattr(repositories_module, "traveler_repository_class")
        event_repository_class = getattr(repositories_module, "event_repository_class")

        self._location_repo = location_repository_class(**kwargs)
        self._traveler_repo = traveler_repository_class(**kwargs)
        self._event_repo = event_repository_class(**kwargs)


class RequestHandlersFactory:
    _location_handler: LocationsRestRequestHandler
    _traveler_handler: TravelersRestRequestHandler
    _event_handler: EventsRestRequestHandler

    @property
    def location_handler(self) -> LocationsRestRequestHandler:
        return self._location_handler

    @property
    def traveler_handler(self) -> TravelersRestRequestHandler:
        return self._traveler_handler

    @property
    def event_handler(self) -> EventsRestRequestHandler:
        return self._event_handler

    def __init__(
            self, rest_controller: RESTController, location_use_case: LocationUseCase, traveler_use_case: TravelerUseCase,
            event_use_case: EventUseCase, timeline_use_case: TimelineUseCase,
    ) -> None:
        self._location_handler = LocationsRestRequestHandler(rest_controller, location_use_case, timeline_use_case)
        self._traveler_handler = TravelersRestRequestHandler(traveler_use_case, timeline_use_case)
        self._event_handler = EventsRestRequestHandler(event_use_case)


class RESTControllersFactory:
    _rest_controller: RESTController

    @property
    def rest_controller(self) -> RESTController:
        return self._rest_controller

    def __init__(self, *, controller_class_path: str, **kwargs) -> None:
        module, class_name = controller_class_path.rsplit(".", maxsplit=1)
        controller_module = import_module(module)
        rest_controller_class = getattr(controller_module, class_name)

        self._rest_controller = rest_controller_class(**kwargs)
