from http import HTTPStatus
from typing import Tuple, Dict, Union, List, Any

from jsonpatch import JsonPatch, InvalidJsonPatch, PatchOperation, make_patch, JsonPatchTestFailed

from adapter.persistence.repositories import InMemoryLocationRepository
from adapter.request_handling.utils import error_response, parse_optional_tag_query_param
from adapter.request_handling.views import LocationView, LocationIdView
from usecase.locations_usecases import LocationUseCase


class LocationsRequestHandler:
    def __init__(self) -> None:
        self._locations_use_case = LocationUseCase(InMemoryLocationRepository())

    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        try:
            location_kwargs = LocationView.kwargs_from_json(request_body)
            location = self._locations_use_case.create(**location_kwargs)
        except KeyError as e:
            return error_response(f"Failed to parse request body: missing attribute {e}", HTTPStatus.BAD_REQUEST)
        except (TypeError, ValueError) as e:
            return error_response(f"Failed to parse request body: {e}", HTTPStatus.BAD_REQUEST)

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
            location = self._locations_use_case.retrieve(location_id)
        except (TypeError, ValueError) as e:
            return error_response(e, HTTPStatus.BAD_REQUEST)
        except NameError as e:
            return error_response(e, HTTPStatus.NOT_FOUND)

        return LocationView.to_json(location), HTTPStatus.OK

    def location_delete_handler(self, location_id_str: str) -> Tuple[Union[dict, str], int]:
        try:
            location_id = LocationIdView.from_json(location_id_str)
            self._locations_use_case.delete(location_id)
        except (TypeError, ValueError) as e:
            return error_response(e, HTTPStatus.BAD_REQUEST)
        except NameError as e:
            return error_response(e, HTTPStatus.NOT_FOUND)

        return "", HTTPStatus.NO_CONTENT

    def location_patch_handler(self, location_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        try:
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
        except NameError as e:
            return error_response(e, HTTPStatus.NOT_FOUND)
        except (TypeError, ValueError, InvalidJsonPatch) as e:
            return error_response(e, HTTPStatus.BAD_REQUEST)
        except JsonPatchTestFailed as e:
            return error_response(e, HTTPStatus.PRECONDITION_FAILED)

        return LocationView.to_json(modified_location), HTTPStatus.OK

    def location_timeline_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        return error_response("Location timeline get not implemented", HTTPStatus.NOT_IMPLEMENTED)
