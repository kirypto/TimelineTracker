from enum import Enum
from functools import total_ordering
from typing import Callable, Tuple, Optional


Route = str
StatusCode = int
VerifierResult = Optional[str]
HandlerResult = Tuple[StatusCode, str]
RequestVerifier = Callable[[...], VerifierResult]
RequestHandler = Callable[[...], HandlerResult]


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


class MIMEType(Enum):
    JSON = "application/json"


class RouteNotFoundError(NameError):
    pass
