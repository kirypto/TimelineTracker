from adapter.factories import RepositoriesFactory
from adapter.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler
from application.location_use_cases import LocationUseCase
from application.traveler_use_cases import TravelerUseCase


class TimelineTrackerApp:
    _locations_request_handler: LocationsRequestHandler
    _travelers_request_handler: TravelersRequestHandler

    @property
    def locations_request_handler(self) -> LocationsRequestHandler:
        return self._locations_request_handler

    @property
    def travelers_request_handler(self) -> TravelersRequestHandler:
        return self._travelers_request_handler

    def __init__(self, *, repositories_config: dict) -> None:
        repositories_factory = RepositoriesFactory(**repositories_config)
        location_use_case = LocationUseCase(repositories_factory.location_repo)
        traveler_use_case = TravelerUseCase(repositories_factory.traveler_repo)
        self._travelers_request_handler = TravelersRequestHandler(traveler_use_case)
        self._locations_request_handler = LocationsRequestHandler(location_use_case)
