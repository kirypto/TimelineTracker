from adapter.factories import RepositoriesFactory
from adapter.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler, EventsRequestHandler
from application.event_use_cases import EventUseCase
from application.location_use_cases import LocationUseCase
from application.timeline_use_cases import TimelineUseCase
from application.traveler_use_cases import TravelerUseCase


class TimelineTrackerApp:
    _locations_request_handler: LocationsRequestHandler
    _travelers_request_handler: TravelersRequestHandler
    _event_request_handler: EventsRequestHandler

    @property
    def locations_request_handler(self) -> LocationsRequestHandler:
        return self._locations_request_handler

    @property
    def travelers_request_handler(self) -> TravelersRequestHandler:
        return self._travelers_request_handler

    @property
    def event_request_handler(self) -> EventsRequestHandler:
        return self._event_request_handler

    def __init__(self, *, repositories_config: dict) -> None:
        repositories_factory = RepositoriesFactory(**repositories_config)
        location_use_case = LocationUseCase(repositories_factory.location_repo, repositories_factory.event_repo)
        traveler_use_case = TravelerUseCase(repositories_factory.traveler_repo, repositories_factory.event_repo)
        event_use_case = EventUseCase(repositories_factory.location_repo, repositories_factory.traveler_repo, repositories_factory.event_repo)
        timeline_use_case = TimelineUseCase(repositories_factory.location_repo, repositories_factory.traveler_repo, repositories_factory.event_repo)
        self._locations_request_handler = LocationsRequestHandler(location_use_case, timeline_use_case)
        self._travelers_request_handler = TravelersRequestHandler(traveler_use_case, timeline_use_case)
        self._event_request_handler = EventsRequestHandler(event_use_case)
