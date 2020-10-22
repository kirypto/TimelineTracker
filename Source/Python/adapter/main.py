from adapter.request_handling.handlers import LocationsRequestHandler


class TimelineTrackerApp:
    _locations_request_handler: LocationsRequestHandler

    @property
    def locations_request_handler(self) -> LocationsRequestHandler:
        return self._locations_request_handler

    def __init__(self) -> None:
        self._locations_request_handler = LocationsRequestHandler()
