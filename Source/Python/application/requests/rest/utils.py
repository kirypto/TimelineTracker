from http import HTTPStatus
from json import loads
from logging import exception
from typing import Union, Tuple, Optional, Set, Callable

from jsonpatch import InvalidJsonPatch, JsonPatchTestFailed, JsonPatchConflict

from application.access.errors import AuthError
from application.requests.data_forms import JsonTranslator
from domain.positions import PositionalRange, Position
from domain.tags import Tag


def error_response(message: Union[str, BaseException], status_code: int) -> Tuple[dict, int]:
    return {"error": str(message)}, status_code


def parse_optional_tag_set_query_param(tags_query_param: Optional[str]) -> Optional[Set[Tag]]:
    if tags_query_param is None:
        return None
    return {JsonTranslator.from_json(tag_str, Tag) for tag_str in tags_query_param.split(",") if len(tag_str) > 0}


def parse_optional_positional_range_query_param(positional_range_query_param: Optional[str]) -> Optional[PositionalRange]:
    if positional_range_query_param is None:
        return None
    return JsonTranslator.from_json(loads(positional_range_query_param), PositionalRange)


def parse_optional_position_query_param(position_query_param: Optional[str]) -> Optional[Position]:
    if position_query_param is None:
        return None
    return JsonTranslator.from_json(loads(position_query_param), Position)


def with_error_response_on_raised_exceptions(handler_function: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            return handler_function(*args, **kwargs)
        except AuthError as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.UNAUTHORIZED)
        except NameError as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.NOT_FOUND)
        except (KeyError, TypeError, ValueError, AttributeError, InvalidJsonPatch) as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.BAD_REQUEST)
        except (JsonPatchTestFailed, JsonPatchConflict) as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.PRECONDITION_FAILED)
        except NotImplementedError as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.NOT_IMPLEMENTED)
        except BaseException as e:
            exception(e, exc_info=e)
            return error_response(e, HTTPStatus.INTERNAL_SERVER_ERROR)

    return inner
