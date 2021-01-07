from flask import request, Flask
from json import dumps

from adapter.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler, EventsRequestHandler


def register_locations_routes(flask_web_app: Flask, locations_request_handler: LocationsRequestHandler) -> None:
    @flask_web_app.route("/api/location", methods=["POST"])
    def api_location__post():
        response_body, status_code = locations_request_handler.locations_post_handler(request.json)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/locations", methods=["GET"])
    def api_locations__get():
        response_body, status_code = locations_request_handler.locations_get_all_handler(dict(request.args))
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["GET"])
    def api_location_id__get(location_id: str):
        response_body, status_code = locations_request_handler.location_get_handler(location_id)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["DELETE"])
    def api_location_id__delete(location_id: str):
        response_body, status_code = locations_request_handler.location_delete_handler(location_id)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["PATCH"])
    def api_location_id__patch(location_id: str):
        response_body, status_code = locations_request_handler.location_patch_handler(location_id, request.json)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/location/<location_id>/timeline", methods=["GET"])
    def api_location_id_timeline__get(location_id: str):
        response_body, status_code = locations_request_handler.location_timeline_get_handler(location_id)
        return dumps(response_body, indent=2), status_code


def register_travelers_routes(flask_web_app: Flask, travelers_request_handler: TravelersRequestHandler) -> None:
    @flask_web_app.route("/api/traveler", methods=["POST"])
    def api_traveler__post():
        response_body, status_code = travelers_request_handler.travelers_post_handler(request.json)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/travelers", methods=["GET"])
    def api_travelers__get():
        response_body, status_code = travelers_request_handler.travelers_get_all_handler(dict(request.args))
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=["GET"])
    def api_traveler_id__get(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_get_handler(traveler_id)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=["DELETE"])
    def api_traveler_id__delete(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_delete_handler(traveler_id)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=["PATCH"])
    def api_traveler_id__patch(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_patch_handler(traveler_id, request.json)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>/timeline", methods=["GET"])
    def api_traveler_id_timeline__get(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_timeline_get_handler(traveler_id)
        return dumps(response_body, indent=2), status_code


def register_events_routes(flask_web_app: Flask, events_request_handler: EventsRequestHandler) -> None:
    @flask_web_app.route("/api/event", methods=["POST"])
    def api_event__post():
        response_body, status_code = events_request_handler.events_post_handler(request.json)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/events", methods=["GET"])
    def api_events__get():
        response_body, status_code = events_request_handler.events_get_all_handler(dict(request.args))
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/event/<event_id>", methods=["GET"])
    def api_event_id__get(event_id: str):
        response_body, status_code = events_request_handler.event_get_handler(event_id)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/event/<event_id>", methods=["DELETE"])
    def api_event_id__delete(event_id: str):
        response_body, status_code = events_request_handler.event_delete_handler(event_id)
        return dumps(response_body, indent=2), status_code

    @flask_web_app.route("/api/event/<event_id>", methods=["PATCH"])
    def api_event_id__patch(event_id: str):
        response_body, status_code = events_request_handler.event_patch_handler(event_id, request.json)
        return dumps(response_body, indent=2), status_code
