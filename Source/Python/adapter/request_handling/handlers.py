from typing import Tuple

from adapter.request_handling.views import LocationView
from usecase.locations_usecases import LocationUseCase


class LocationsRequestHandler:
    def __init__(self):
        self._locations_use_case = LocationUseCase()

    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        try:
            location = self._locations_use_case.create_location(**request_body)
            return LocationView.to_json(location), 200
        except (TypeError, ValueError) as e:
            return {"error": str(e)}, 400
