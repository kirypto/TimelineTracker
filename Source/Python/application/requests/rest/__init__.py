from enum import Enum
from functools import total_ordering
from typing import Union, Callable, Any, Tuple, Optional


Route = str
StatusCode = int
Data = Union[str, dict]
RequestVerifier = Callable[[Any], Tuple[bool, Optional[str]]]
RequestHandler = Callable[[Any], Tuple[StatusCode, Data]]


@total_ordering
class RESTMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, RESTMethod):
            return NotImplemented
        other_method: RESTMethod = other
        for method in RESTMethod:
            if self == method:
                return False
            elif other_method == method:
                return True
        return False


RouteDescriptor = Tuple[Route, RESTMethod, RequestVerifier, RequestHandler]


class RouteNotFoundError(NameError):
    pass
