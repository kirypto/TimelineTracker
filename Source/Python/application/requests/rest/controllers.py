import re
from abc import ABC, abstractmethod
from inspect import getfullargspec
from typing import Callable

from application.requests.rest import RESTMethod, RequestHandler, MIMEType


HandlerRegisterer = Callable[[RequestHandler], None]
_ROUTE_URL_PARAM_PATTERN = re.compile("<([a-zA-Z_]+)>")


def validate_handler_accepts_route_url_parameters(route: str, handler: RequestHandler) -> None:
    handler_argument_spec = getfullargspec(handler)
    route_url_parameters = re.findall(_ROUTE_URL_PARAM_PATTERN, route)
    for url_param in route_url_parameters:
        if url_param not in handler_argument_spec.kwonlyargs:
            raise ValueError(f"Failed to register route {route}, provided handler does not accept '{url_param}' as a keyword-only arg.")


class RESTController(ABC):
    @abstractmethod
    def register_rest_endpoint(
            self, route: str, method: RESTMethod, response_type: MIMEType = MIMEType.JSON, *, json: bool = False, query_params: bool = False
    ) -> HandlerRegisterer:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass
