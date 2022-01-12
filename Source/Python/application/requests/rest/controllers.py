from collections import defaultdict
from logging import error
from typing import Dict, Set, Tuple

from application.requests.rest import Route, RESTMethod, RequestVerifier, RequestHandler, StatusCode, Data, RouteNotFoundError
from application.requests.rest.handlers import AbstractRESTHandler


class RESTController:
    _supported_routes: Dict[Route, Set[RESTMethod]]
    _request_verifiers: Dict[Route, Dict[RESTMethod, RequestVerifier]]
    _request_handlers: Dict[Route, Dict[RESTMethod, RequestHandler]]

    def __init__(self, handlers: Set[AbstractRESTHandler]) -> None:
        self._validate_handlers(handlers)
        self._supported_routes = defaultdict(set)
        self._request_verifiers = defaultdict(dict)
        self._request_handlers = defaultdict(dict)
        for handler in handlers:
            for route, http_method, verifier_function, handler_function in handler.get_routes():
                self._supported_routes[route].add(http_method)
                self._request_verifiers[route][http_method] = verifier_function
                self._request_handlers[route][http_method] = handler_function

    def handle(self, route: Route, method: RESTMethod, *args, **kwargs) -> Tuple[StatusCode, Data]:
        if route not in self._supported_routes or method not in self._supported_routes[route]:
            error(f"No handler registered for '{method.value} {route}'")
            raise RouteNotFoundError(f"Unsupported resource '{method.value} {route}'")

        request_verifier = self._request_verifiers[route][method]
        is_valid, message_if_invalid = request_verifier(*args, **kwargs)
        if not is_valid:
            error(f"Handler for '{method.value} {route}' rejected provided arguments: {message_if_invalid}")
            raise ValueError(message_if_invalid)

        request_handler = self._request_handlers[route][method]
        status_code, data = request_handler(*args, **kwargs)
        return status_code, data

    def get_supported_resources(self) -> Set[Tuple[Route, RESTMethod]]:
        supported_routes: Set[Tuple[Route, RESTMethod]] = set()
        for route, methods in self._supported_routes.items():
            for method in methods:
                supported_routes.add((route, method))
        return supported_routes

    @staticmethod
    def _validate_handlers(handlers: Set[AbstractRESTHandler]) -> None:
        handler_routes = sorted([(route, http_method) for handler in handlers for route, http_method, _, _ in handler.get_routes()])
        for index in range(len(handler_routes) - 1):
            if handler_routes[index] == handler_routes[index + 1]:
                curr_route, curr_type = handler_routes[index]
                raise ValueError(f"Multiple {AbstractRESTHandler.__name__}s register {curr_type.value} for route {curr_route}.")
