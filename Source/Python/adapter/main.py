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

    def __init__(self) -> None:
        self._travelers_request_handler = TravelersRequestHandler()
        self._locations_request_handler = LocationsRequestHandler()
