from http import HTTPStatus
from typing import Tuple, Dict, Union

from adapter.persistence.repositories import InMemoryLocationRepository
from adapter.request_handling.utils import error_response, parse_optional_tag_query_param
from adapter.request_handling.views import LocationView, LocationIdView
from usecase.locations_usecases import LocationUseCase


class LocationsRequestHandler:
    def __init__(self):
        self._locations_use_case = LocationUseCase(InMemoryLocationRepository())

    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        try:
            location_kwargs = LocationView.from_json(request_body)
        except KeyError as e:
            return error_response(f"Failed to parse request body: missing attribute {e}", HTTPStatus.BAD_REQUEST)
        except ValueError as e:
            return error_response(f"Failed to parse request body: {e}", HTTPStatus.BAD_REQUEST)

        try:
            location = self._locations_use_case.create(**location_kwargs)
        except (TypeError, ValueError) as e:
            return error_response(e, HTTPStatus.BAD_REQUEST)

        return LocationView.to_json(location), HTTPStatus.CREATED

    def locations_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        try:
            filters = {
                "name": query_params.get("name", None),
                "tagged_with_all": parse_optional_tag_query_param(query_params.get("taggedAll", None)),
                "tagged_with_any": parse_optional_tag_query_param(query_params.get("taggedAny", None)),
                "tagged_with_only": parse_optional_tag_query_param(query_params.get("taggedOnly", None)),
                "tagged_with_none": parse_optional_tag_query_param(query_params.get("taggedNone", None)),
            }
        except (TypeError, ValueError, AttributeError) as e:
            return error_response(e, HTTPStatus.BAD_REQUEST)

        locations = self._locations_use_case.retrieve_all(**filters)

        return [LocationIdView.to_json(location.id) for location in locations], HTTPStatus.OK

    def location_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        try:
            location_id = LocationIdView.from_json(location_id_str)
        except (TypeError, ValueError) as e:
            return error_response(e, HTTPStatus.BAD_REQUEST)

        location = self._locations_use_case.retrieve(location_id)

        if location is None:
            return error_response(f"No location found with id '{location_id}'", HTTPStatus.NOT_FOUND)

        return LocationView.to_json(location), HTTPStatus.OK

    def location_delete_handler(self, location_id_str: str) -> Tuple[dict, int]:
        return error_response("Location delete not implemented", HTTPStatus.NOT_IMPLEMENTED)

    def location_patch_handler(self, location_id_str: str) -> Tuple[dict, int]:
        return error_response("Location patch not implemented", HTTPStatus.NOT_IMPLEMENTED)

    def location_timeline_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        return error_response("Location timeline get not implemented", HTTPStatus.NOT_IMPLEMENTED)

