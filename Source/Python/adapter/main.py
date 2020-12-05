from adapter.factories import RepositoriesFactory
from adapter.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler


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
        self._travelers_request_handler = TravelersRequestHandler(repositories_factory.traveler_repo)
        self._locations_request_handler = LocationsRequestHandler(repositories_factory.location_repo)
