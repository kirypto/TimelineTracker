from http import HTTPStatus
from typing import Tuple, Dict, Union, List, Any

from adapter.request_handling.utils import parse_optional_tag_query_param, with_error_response_on_raised_exceptions, process_patch_into_delta_kwargs
from adapter.views import LocationView, LocationIdView, TravelerView, TravelerIdView
from application.location_use_cases import LocationUseCase
from application.traveler_use_cases import TravelerUseCase


class LocationsRequestHandler:
    def __init__(self, location_use_case: LocationUseCase) -> None:
        self._location_use_case = location_use_case

    @with_error_response_on_raised_exceptions
    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        location_kwargs = LocationView.kwargs_from_json(request_body)
        location = self._location_use_case.create(**location_kwargs)

        return LocationView.to_json(location), HTTPStatus.CREATED

    @with_error_response_on_raised_exceptions
    def locations_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        supported_filters = {"nameIs", "nameHas", "taggedAll", "taggedAny", "taggedOnly", "taggedNone"}
        if not set(query_params.keys()).issubset(supported_filters):
            raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
        filters = {
            "name_is": query_params.get("nameIs", None),
            "name_has": query_params.get("nameHas", None),
            "tagged_all": parse_optional_tag_query_param(query_params.get("taggedAll", None)),
            "tagged_any": parse_optional_tag_query_param(query_params.get("taggedAny", None)),
            "tagged_only": parse_optional_tag_query_param(query_params.get("taggedOnly", None)),
            "tagged_none": parse_optional_tag_query_param(query_params.get("taggedNone", None)),
        }

        locations = self._location_use_case.retrieve_all(**filters)

        return [LocationIdView.to_json(location.id) for location in locations], HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def location_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        location_id = LocationIdView.from_json(location_id_str)
        location = self._location_use_case.retrieve(location_id)

        return LocationView.to_json(location), HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def location_delete_handler(self, location_id_str: str) -> Tuple[Union[dict, str], int]:
        location_id = LocationIdView.from_json(location_id_str)
        self._location_use_case.delete(location_id)

        return "", HTTPStatus.NO_CONTENT

    @with_error_response_on_raised_exceptions
    def location_patch_handler(self, location_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        location_id = LocationIdView.from_json(location_id_str)

        existing_location = self._location_use_case.retrieve(location_id)
        delta_kwargs = process_patch_into_delta_kwargs(existing_location, patch_operations, LocationView)
        modified_location = self._location_use_case.update(location_id, **delta_kwargs)

        return LocationView.to_json(modified_location), HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def location_timeline_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        raise NotImplementedError("Location timeline get not implemented")


class TravelersRequestHandler:
    def __init__(self, traveler_use_case: TravelerUseCase) -> None:
        self._traveler_use_case = traveler_use_case

    @with_error_response_on_raised_exceptions
    def travelers_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        traveler_kwargs = TravelerView.kwargs_from_json(request_body)
        traveler = self._traveler_use_case.create(**traveler_kwargs)

        return TravelerView.to_json(traveler), HTTPStatus.CREATED

    @with_error_response_on_raised_exceptions
    def travelers_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        supported_filters = {"nameIs", "nameHas", "taggedAll", "taggedAny", "taggedOnly", "taggedNone"}
        if not set(query_params.keys()).issubset(supported_filters):
            raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
        filters = {
            "name_is": query_params.get("nameIs", None),
            "name_has": query_params.get("nameHas", None),
            "tagged_all": parse_optional_tag_query_param(query_params.get("taggedAll", None)),
            "tagged_any": parse_optional_tag_query_param(query_params.get("taggedAny", None)),
            "tagged_only": parse_optional_tag_query_param(query_params.get("taggedOnly", None)),
            "tagged_none": parse_optional_tag_query_param(query_params.get("taggedNone", None)),
        }

        travelers = self._traveler_use_case.retrieve_all(**filters)

        return [TravelerIdView.to_json(traveler.id) for traveler in travelers], HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def traveler_get_handler(self, traveler_id_str: str) -> Tuple[dict, int]:
        traveler_id = TravelerIdView.from_json(traveler_id_str)
        traveler = self._traveler_use_case.retrieve(traveler_id)

        return TravelerView.to_json(traveler), HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def traveler_delete_handler(self, traveler_id_str: str) -> Tuple[Union[dict, str], int]:
        traveler_id = LocationIdView.from_json(traveler_id_str)
        self._traveler_use_case.delete(traveler_id)

        return "", HTTPStatus.NO_CONTENT

    @with_error_response_on_raised_exceptions
    def traveler_patch_handler(self, traveler_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        traveler_id = TravelerIdView.from_json(traveler_id_str)

        existing_traveler = self._traveler_use_case.retrieve(traveler_id)
        delta_kwargs = process_patch_into_delta_kwargs(existing_traveler, patch_operations, TravelerView)
        modified_traveler = self._traveler_use_case.update(traveler_id, **delta_kwargs)

        return TravelerView.to_json(modified_traveler), HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def traveler_timeline_get_handler(self, traveler_id_str: str) -> Tuple[dict, int]:
        raise NotImplementedError("Traveler timeline get not implemented")
