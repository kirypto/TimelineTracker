from http import HTTPStatus
from json import loads
from logging import exception
from typing import Union, Tuple, Optional, Set, Callable, Any, List, Dict, Type

from jsonpatch import InvalidJsonPatch, JsonPatchTestFailed, JsonPatch, PatchOperation, make_patch

from adapter.views import DomainConstructedView, ValueTranslator
from domain.positions import PositionalRange, Position
from domain.tags import Tag


def error_response(message: Union[str, BaseException], status_code: int) -> Tuple[dict, int]:
    return {"error": str(message)}, status_code


def parse_optional_tag_set_query_param(tags_query_param: Optional[str]) -> Optional[Set[Tag]]:
    if tags_query_param is None:
        return None
    return {ValueTranslator.from_json(tag_str, Tag) for tag_str in tags_query_param.split(",") if len(tag_str) > 0}


def parse_optional_positional_range_query_param(positional_range_query_param: Optional[str]) -> Optional[PositionalRange]:
    if positional_range_query_param is None:
        return None
    return ValueTranslator.from_json(loads(positional_range_query_param), PositionalRange)


def parse_optional_position_query_param(position_query_param: Optional[str]) -> Optional[Position]:
    if position_query_param is None:
        return None
    return ValueTranslator.from_json(loads(position_query_param), Position)


def with_error_response_on_raised_exceptions(handler_function: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            return handler_function(*args, **kwargs)
        except NameError as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.NOT_FOUND)
        except (KeyError, TypeError, ValueError, AttributeError, InvalidJsonPatch) as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.BAD_REQUEST)
        except JsonPatchTestFailed as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.PRECONDITION_FAILED)
        except NotImplementedError as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.NOT_IMPLEMENTED)
        except BaseException as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.INTERNAL_SERVER_ERROR)

    return inner


def process_patch_into_delta_kwargs(existing_object: Any, patch_operations: List[Dict[str, Any]], view_type: Type[DomainConstructedView]) -> Dict[
    str, Any]:
    patch = JsonPatch([PatchOperation(operation).operation for operation in patch_operations])

    existing_object_view = view_type.to_json(existing_object)
    modified_object_view = patch.apply(existing_object_view)

    names_of_modified_attributes = [
        change["path"][1:].split("/")[0]  # The JsonPatch object's 'path', extract only first delimited portion. Ex: '/foo/bar/0' -> 'foo'
        for change in make_patch(existing_object_view, modified_object_view)  # Use make_patch to determine the differences
    ]
    delta_kwargs = {
        kwarg_name: kwarg_value
        for kwarg_name, kwarg_value in view_type.kwargs_from_json(modified_object_view).items()
        if kwarg_name in names_of_modified_attributes
    }
    return delta_kwargs
