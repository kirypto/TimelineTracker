from collections import defaultdict
from functools import wraps
from json import dumps
from typing import Optional, Dict, Callable

from flask import request, Flask, make_response, Response

from adapter.auth.auth0 import extract_profile_from_flask_session
from application.access.clients import Profile
from application.requests.rest import RESTMethod, HandlerResult, RequestHandler, MIMEType
from application.requests.rest.controllers import RESTController, HandlerRegisterer, validate_route_handler_declaration
from application.requests.rest.handlers import LocationsRestRequestHandler, TravelersRestRequestHandler, EventsRestRequestHandler
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
                rest_method = RESTMethod(request.method.upper())
                return method_handler_dict[rest_method](*args, **kwargs)

            self._flask_web_app.add_url_rule(route, route, route_handler, methods=[m.value for m in method_handler_dict.keys()])

        self._finalized = True


def register_locations_routes(flask_web_app: Flask, locations_request_handler: LocationsRestRequestHandler) -> None:
    @flask_web_app.route("/api/locations", methods=[_HTTPMethod.Get])
    @extract_profile_from_flask_session
    def api_locations__get(*, profile: Optional[Profile]):
        response_body, status_code = locations_request_handler.locations_get_all_handler(dict(request.args), profile=profile)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=[_HTTPMethod.Get, _HTTPMethod.Patch, _HTTPMethod.Delete])
    @extract_profile_from_flask_session
    def api_location_id__get_patch_post(location_id: str, *, profile: Optional[Profile]):
        if request.method == _HTTPMethod.Get:
            response_body, status_code = locations_request_handler.location_get_handler(location_id, profile=profile)
        elif request.method == _HTTPMethod.Patch:
            response_body, status_code = locations_request_handler.location_patch_handler(location_id, request.json, profile=profile)
        elif request.method == _HTTPMethod.Delete:
            response_body, status_code = locations_request_handler.location_delete_handler(location_id, profile=profile)
        else:
            raise ValueError(f"Route does not support {request.method}")
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/location/<location_id>/timeline", methods=[_HTTPMethod.Get])
    @extract_profile_from_flask_session
    def api_location_id_timeline__get(location_id: str, *, profile: Optional[Profile]):
        response_body, status_code = locations_request_handler.location_timeline_get_handler(
            location_id, dict(request.args), profile=profile)
        return dumps(response_body, indent=2), status_code


def register_travelers_routes(flask_web_app: Flask, travelers_request_handler: TravelersRestRequestHandler) -> None:
    @flask_web_app.route("/api/traveler", methods=[_HTTPMethod.Post])
    @extract_profile_from_flask_session
    def api_traveler__post(*, profile: Optional[Profile]):
        response_body, status_code = travelers_request_handler.travelers_post_handler(request.json, profile=profile)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/travelers", methods=[_HTTPMethod.Get])
    @extract_profile_from_flask_session
    def api_travelers__get(*, profile: Optional[Profile]):
        response_body, status_code = travelers_request_handler.travelers_get_all_handler(dict(request.args), profile=profile)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=[_HTTPMethod.Get, _HTTPMethod.Patch, _HTTPMethod.Delete])
    @extract_profile_from_flask_session
    def api_traveler_id__get_patch_post(traveler_id: str, *, profile: Optional[Profile]):
        if request.method == _HTTPMethod.Get:
            response_body, status_code = travelers_request_handler.traveler_get_handler(traveler_id, profile=profile)
        elif request.method == _HTTPMethod.Patch:
            response_body, status_code = travelers_request_handler.traveler_patch_handler(traveler_id, request.json, profile=profile)
        elif request.method == _HTTPMethod.Delete:
            response_body, status_code = travelers_request_handler.traveler_delete_handler(traveler_id, profile=profile)
        else:
            raise ValueError(f"Route does not support {request.method}")
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>/journey", methods=[_HTTPMethod.Post])
    @extract_profile_from_flask_session
    def api_traveler_id_journey__post(traveler_id: str, *, profile: Optional[Profile]):
        response_body, status_code = travelers_request_handler.traveler_journey_post_handler(traveler_id, request.json, profile=profile)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>/timeline", methods=[_HTTPMethod.Get])
    @extract_profile_from_flask_session
    def api_traveler_id_timeline__get(traveler_id: str, *, profile: Optional[Profile]):
        response_body, status_code = travelers_request_handler.traveler_timeline_get_handler(
            traveler_id, dict(request.args), profile=profile)
        return dumps(response_body, indent=2), status_code


def register_events_routes(flask_web_app: Flask, events_request_handler: EventsRestRequestHandler) -> None:
    @flask_web_app.route("/api/event", methods=[_HTTPMethod.Post])
    @extract_profile_from_flask_session
    def api_event__post(*, profile: Optional[Profile]):
        response_body, status_code = events_request_handler.events_post_handler(request.json, profile=profile)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/events", methods=[_HTTPMethod.Get])
    @extract_profile_from_flask_session
    def api_events__get(*, profile: Optional[Profile]):
        response_body, status_code = events_request_handler.events_get_all_handler(dict(request.args), profile=profile)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/event/<event_id>", methods=[_HTTPMethod.Get, _HTTPMethod.Patch, _HTTPMethod.Delete])
    @extract_profile_from_flask_session
    def api_event_id__get_patch_post(event_id: str, *, profile: Optional[Profile]):
        if request.method == _HTTPMethod.Get:
            response_body, status_code = events_request_handler.event_get_handler(event_id, profile=profile)
        elif request.method == _HTTPMethod.Patch:
            response_body, status_code = events_request_handler.event_patch_handler(event_id, request.json, profile=profile)
        elif request.method == _HTTPMethod.Delete:
            response_body, status_code = events_request_handler.event_delete_handler(event_id, profile=profile)
        else:
            raise ValueError(f"Route does not support {request.method}")
        return dumps(response_body, indent=2), status_code
