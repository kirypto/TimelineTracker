from http import HTTPStatus
from logging import exception
from typing import Union, Tuple, Optional, Set, Callable

from jsonpatch import InvalidJsonPatch, JsonPatchTestFailed

from domain.tags import Tag


def error_response(message: Union[str, BaseException], status_code: int) -> Tuple[dict, int]:
    return {"error": str(message)}, status_code


def parse_optional_tag_query_param(tag_query_param: Optional[str]) -> Optional[Set[Tag]]:
    if tag_query_param is None:
        return None
    return {Tag(tag_str) for tag_str in tag_query_param.split(",") if len(tag_str) > 0}


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
