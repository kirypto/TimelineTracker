from http import HTTPStatus
from typing import Tuple, Dict, Any

from adapter.persistence.repositories import InMemoryLocationRepository
from adapter.request_handling.utils import error_response, parse_optional_tag_query_param
from adapter.request_handling.views import LocationView, PrefixedUUIDView
from usecase.locations_usecases import LocationUseCase


class LocationsRequestHandler:
    def __init__(self):
        self._locations_use_case = LocationUseCase(InMemoryLocationRepository())

    def locations_post_handler(self, request_body: dict) -> Tuple[Any, int]:
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

    def locations_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Any, int]:
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

        return [PrefixedUUIDView.to_json(location.id) for location in locations], HTTPStatus.OK
