from collections import defaultdict
from functools import wraps
from typing import Dict, Callable

from flask import request, Flask, make_response, Response

from adapter.auth.auth0 import extract_profile_from_flask_session
from application.requests.rest import RESTMethod, HandlerResult, RequestHandler, MIMEType
from application.requests.rest.controllers import RESTController, HandlerRegisterer, validate_route_handler_declaration
from application.requests.rest.utils import with_error_response_on_raised_exceptions


class _HTTPMethod:
    Post = "POST"
    Get = "GET"
    Delete = "DELETE"
    Patch = "PATCH"


class FlaskRESTController(RESTController):
    _flask_web_app: Flask
    _finalized: bool
    _routes: Dict[str, Dict[RESTMethod, Callable]]

    def __init__(self, *, flask_web_app: Flask) -> None:
        self._flask_web_app = flask_web_app
        self._finalized = False
        self._routes = defaultdict(dict)

    def register_rest_endpoint(
            self, route: str, method: RESTMethod, response_type: MIMEType = MIMEType.JSON, *, json: bool = False, query_params: bool = False
    ) -> HandlerRegisterer:
        if self._finalized:
            raise ValueError("Cannot register, controller has already been finalized.")
        if not isinstance(route, str):
            raise ValueError(f"Cannot register, route argument must be a str but was {type(route)}.")
        if not isinstance(method, RESTMethod):
            raise ValueError(f"Cannot register, method argument must be a {type(RESTMethod).__name__} but was {type(route)}.")
        if method in self._routes[route]:
            # TODO kirypto 2022-Feb24: Ensure tests exist for this
            raise ValueError(f"Cannot register, method {method} already registered for {route}")

        def handler_registerer(handler_func: RequestHandler) -> None:
            validate_route_handler_declaration(route, handler_func)

            @with_error_response_on_raised_exceptions
            @extract_profile_from_flask_session
            @wraps(handler_func)
            def handler_wrapper(**kwargs) -> Response:
                args = []
                if json:
                    if request.json is None:
                        raise ValueError("Json body must be provided")
                    args.append(request.json)
                if query_params:
                    args.append(dict(request.args))

                response: HandlerResult = handler_func(*args, **kwargs)
                status_code, contents = response
                flask_response = make_response(contents, status_code)
                flask_response.mimetype = response_type.value
                return flask_response

            self._routes[route][method] = handler_wrapper

        return handler_registerer

    def finalize(self) -> None:
        if self._finalized:
            raise ValueError("Controller has already been finalized.")

        for route, method_handler_dict in self._routes.items():
            def route_handler(*args, **kwargs):
                request_url = request.url_rule.rule
                rest_method = RESTMethod(request.method.upper())
                return self._routes[request_url][rest_method](*args, **kwargs)

            self._flask_web_app.add_url_rule(route, route, route_handler, methods=[m.value for m in method_handler_dict.keys()])

        self._finalized = True

