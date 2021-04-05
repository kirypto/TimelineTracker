from importlib import import_module

from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from domain.persistence.repositories import TravelerRepository, LocationRepository, EventRepository
from domain.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler, EventsRequestHandler


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
    _HANDLER_TYPES = {
        "rest": "rest_handlers",
    }
    _location_handler: LocationsRequestHandler
    _traveler_handler: TravelersRequestHandler
    _event_handler: EventsRequestHandler

    @property
    def location_handler(self) -> LocationsRequestHandler:
        return self._location_handler

    @property
    def traveler_handler(self) -> TravelersRequestHandler:
        return self._traveler_handler

    @property
    def event_handler(self) -> EventsRequestHandler:
        return self._event_handler

    def __init__(self, location_use_case: LocationUseCase, traveler_use_case: TravelerUseCase, event_use_case: EventUseCase,
                 timeline_use_case: TimelineUseCase, request_handler_type: str) -> None:
        if request_handler_type not in RequestHandlersFactory._HANDLER_TYPES:
            raise ValueError(f"Unsupported request handler type {request_handler_type}. "
                             f"Supported types are: {set(RequestHandlersFactory._HANDLER_TYPES.keys())}")

        request_handlers_module = import_module(f"adapter.request_handling.{RequestHandlersFactory._HANDLER_TYPES[request_handler_type]}")
        location_request_handler_class = getattr(request_handlers_module, "location_request_handler_class")
        traveler_request_handler_class = getattr(request_handlers_module, "traveler_request_handler_class")
        event_request_handler_class = getattr(request_handlers_module, "event_request_handler_class")

        self._location_handler = location_request_handler_class(location_use_case, timeline_use_case)
        self._traveler_handler = traveler_request_handler_class(traveler_use_case, timeline_use_case)
        self._event_handler = event_request_handler_class(event_use_case)
