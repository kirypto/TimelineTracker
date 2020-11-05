from http import HTTPStatus
from typing import Tuple

from adapter.request_handling.views import LocationView
from usecase.locations_usecases import LocationUseCase


class LocationsRequestHandler:
    def __init__(self):
        self._locations_use_case = LocationUseCase()

    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        try:
            location_kwargs = LocationView.from_json(request_body)
        except KeyError as e:
            return {"error": f"Failed to parse request body: missing attribute {e}"}, HTTPStatus.BAD_REQUEST
        except ValueError as e:
            return {"error": f"Failed to parse request body: {e}"}, HTTPStatus.BAD_REQUEST

        try:
            location = self._locations_use_case.create(**location_kwargs)
        except (TypeError, ValueError) as e:
            return {"error": str(e)}, HTTPStatus.BAD_REQUEST

        return LocationView.to_json(location), HTTPStatus.CREATED
