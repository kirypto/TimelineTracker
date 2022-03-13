from collections import defaultdict
from typing import Any, Dict

from application.requests.rest import RESTMethod, MIMEType, RequestHandler, HandlerResult
from application.requests.rest.controllers import RESTController, HandlerRegisterer, validate_route_handler_declaration
from application.requests.rest.utils import with_error_response_on_raised_exceptions


class TestableRESTController(RESTController):
    _handlers: Dict[str, Dict[RESTMethod, RequestHandler]]

    def __init__(self):
        self._handlers = defaultdict(dict)

    def register_rest_endpoint(self, route: str, method: RESTMethod, response_type: MIMEType = MIMEType.JSON, *, json: bool = False,
                               query_params: bool = False) -> HandlerRegisterer:
        def handler_registerer(handler_func: RequestHandler) -> None:
            validate_route_handler_declaration(route, handler_func)

            @with_error_response_on_raised_exceptions
            def handler_wrapper(*args, **kwargs) -> HandlerResult:
                return handler_func(*args, **kwargs)

            self._handlers[route][method] = handler_wrapper

        return handler_registerer

    def finalize(self) -> None:
        pass

    def invoke(self, route: str, method: RESTMethod, *, json: Any = None, query_params: Dict[str, Any] = None) -> HandlerResult:
        args = []
        if json is not None:
            args.append(json)
        if query_params is not None:
            args.append(query_params)
        return self._handlers[route][method](*args)
