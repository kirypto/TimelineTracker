from functools import wraps
from json import dumps
from typing import Optional, Tuple, Any

from flask import request, Flask

from adapter.auth.auth0 import extract_profile_from_flask_session
from application.access.clients import Profile
from application.requests.rest import RESTMethod, HandlerResult, RequestHandler
from application.requests.rest.controllers import RESTController, HandlerRegisterer
from application.requests.rest.handlers import LocationsRestRequestHandler, TravelersRestRequestHandler, EventsRestRequestHandler
from application.requests.rest.utils import with_error_response_on_raised_exceptions


class _HTTPMethod:
    Post = "POST"
    Get = "GET"
    Delete = "DELETE"
    Patch = "PATCH"


class FlaskRESTController(RESTController):
    _flask_web_app: Flask

    def __init__(self, *, flask_web_app: Flask) -> None:
        self._flask_web_app = flask_web_app

    def register_rest_endpoint(
            self, route: str, method: RESTMethod, *, json: bool = False, query_params: bool = False
    ) -> HandlerRegisterer:
        def handler_registerer(handler_func: RequestHandler) -> None:

            @with_error_response_on_raised_exceptions
            @extract_profile_from_flask_session
            @wraps(handler_func)
            def handler_wrapper(**kwargs) -> Tuple[Any, int]:
                args = []
                if json:
                    if request.json is None:
                        raise ValueError("Json body must be provided")
                    args.append(request.json)
                if query_params:
                    args.append(dict(request.args))

                response: HandlerResult = handler_func(*args, **kwargs)
                status_code, contents = response
                return contents, status_code

            self._flask_web_app.add_url_rule(route, route, handler_wrapper)

        return handler_registerer


def register_locations_routes(flask_web_app: Flask, locations_request_handler: LocationsRestRequestHandler) -> None:
    @flask_web_app.route("/api/location", methods=[_HTTPMethod.Post])
    @extract_profile_from_flask_session
    def api_location__post(*, profile: Optional[Profile]):
        response_body, status_code = locations_request_handler.locations_post_handler(request.json, profile=profile)
        return dumps(response_body, indent=2), status_code

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
