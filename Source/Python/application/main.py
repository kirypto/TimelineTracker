from _version import __version__
from application.factories import RepositoriesFactory, RequestHandlersFactory
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from domain.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler, EventsRequestHandler


class TimelineTrackerApp:
    _version: str
    _locations_request_handler: LocationsRequestHandler
    _travelers_request_handler: TravelersRequestHandler
    _event_request_handler: EventsRequestHandler

    @property
    def version(self) -> str:
        return __version__

    @property
    def locations_request_handler(self) -> LocationsRequestHandler:
        return self._locations_request_handler

    @property
    def travelers_request_handler(self) -> TravelersRequestHandler:
        return self._travelers_request_handler

    @property
    def event_request_handler(self) -> EventsRequestHandler:
        return self._event_request_handler

    def __init__(self, *, repositories_config: dict, request_handlers_config: dict) -> None:
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
