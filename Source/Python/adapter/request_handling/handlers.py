from http import HTTPStatus
from typing import Tuple, Dict, Union, List, Any

from jsonpatch import JsonPatch, PatchOperation, make_patch

from adapter.persistence.in_memory_repositories import InMemoryLocationRepository
from adapter.request_handling.utils import parse_optional_tag_query_param, with_error_response_on_raised_exceptions
from adapter.views import LocationView, LocationIdView
from usecase.locations_usecases import LocationUseCase


class LocationsRequestHandler:
    def __init__(self) -> None:
        self._locations_use_case = LocationUseCase(InMemoryLocationRepository())

    @with_error_response_on_raised_exceptions
    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        location_kwargs = LocationView.kwargs_from_json(request_body)
        location = self._locations_use_case.create(**location_kwargs)

        return LocationView.to_json(location), HTTPStatus.CREATED

    @with_error_response_on_raised_exceptions
    def locations_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        filters = {
            "name": query_params.get("name", None),
            "tagged_with_all": parse_optional_tag_query_param(query_params.get("taggedAll", None)),
            "tagged_with_any": parse_optional_tag_query_param(query_params.get("taggedAny", None)),
            "tagged_with_only": parse_optional_tag_query_param(query_params.get("taggedOnly", None)),
            "tagged_with_none": parse_optional_tag_query_param(query_params.get("taggedNone", None)),
        }

        locations = self._locations_use_case.retrieve_all(**filters)

        return [LocationIdView.to_json(location.id) for location in locations], HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def location_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        location_id = LocationIdView.from_json(location_id_str)
        location = self._locations_use_case.retrieve(location_id)

        return LocationView.to_json(location), HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def location_delete_handler(self, location_id_str: str) -> Tuple[Union[dict, str], int]:
        location_id = LocationIdView.from_json(location_id_str)
        self._locations_use_case.delete(location_id)

        return "", HTTPStatus.NO_CONTENT

    @with_error_response_on_raised_exceptions
    def location_patch_handler(self, location_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        location_id = LocationIdView.from_json(location_id_str)
        patch = JsonPatch([PatchOperation(operation).operation for operation in patch_operations])

        existing_location = self._locations_use_case.retrieve(location_id)

        existing_location_view = LocationView.to_json(existing_location)
        modified_json_object = patch.apply(existing_location_view)
        changed_attributes = [change["path"][1:].split("/")[0] for change in (make_patch(existing_location_view, modified_json_object))]
        delta_kwargs = {
            kwarg_name: kwarg_value
            for kwarg_name, kwarg_value in LocationView.kwargs_from_json(modified_json_object).items()
            if kwarg_name in changed_attributes
        }

        modified_location = self._locations_use_case.update(location_id, **delta_kwargs)

        return LocationView.to_json(modified_location), HTTPStatus.OK

    @with_error_response_on_raised_exceptions
    def location_timeline_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        raise NotImplementedError("Location timeline get not implemented")


class TravelersRequestHandler:
    @with_error_response_on_raised_exceptions
    def travelers_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        raise NotImplementedError("travelers post not implemented")

    @with_error_response_on_raised_exceptions
    def travelers_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        raise NotImplementedError("travelers get all not implemented")

    @with_error_response_on_raised_exceptions
    def traveler_get_handler(self, traveler_id_str: str) -> Tuple[dict, int]:
        raise NotImplementedError("traveler get not implemented")

    @with_error_response_on_raised_exceptions
    def traveler_delete_handler(self, traveler_id_str: str) -> Tuple[Union[dict, str], int]:
        raise NotImplementedError("traveler delete not implemented")

    @with_error_response_on_raised_exceptions
    def traveler_patch_handler(self, traveler_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        raise NotImplementedError("traveler patch not implemented")

    @with_error_response_on_raised_exceptions
    def traveler_timeline_get_handler(self, traveler_id_str: str) -> Tuple[dict, int]:
        raise NotImplementedError("Traveler timeline get not implemented")
