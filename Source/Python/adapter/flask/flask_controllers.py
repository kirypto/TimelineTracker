from flask import request, Flask, jsonify

from adapter.request_handling.handlers import LocationsRequestHandler, TravelersRequestHandler


def register_locations_routes(flask_web_app: Flask, locations_request_handler: LocationsRequestHandler) -> None:
    @flask_web_app.route("/api/location", methods=["POST"])
    def api_location__post():
        response_body, status_code = locations_request_handler.locations_post_handler(request.json)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/locations", methods=["GET"])
    def api_locations__get():
        response_body, status_code = locations_request_handler.locations_get_all_handler(dict(request.args))
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["GET"])
    def api_location_id__get(location_id: str):
        response_body, status_code = locations_request_handler.location_get_handler(location_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["DELETE"])
    def api_location_id__delete(location_id: str):
        response_body, status_code = locations_request_handler.location_delete_handler(location_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["PATCH"])
    def api_location_id__patch(location_id: str):
        response_body, status_code = locations_request_handler.location_patch_handler(location_id, request.json)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>/timeline", methods=["GET"])
    def api_location_id_timeline__get(location_id: str):
        response_body, status_code = locations_request_handler.location_timeline_get_handler(location_id)
        return jsonify(response_body), status_code


def register_travelers_routes(flask_web_app: Flask, travelers_request_handler: TravelersRequestHandler) -> None:
    @flask_web_app.route("/api/traveler", methods=["POST"])
    def api_traveler__post():
        response_body, status_code = travelers_request_handler.travelers_post_handler(request.json)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/travelers", methods=["GET"])
    def api_travelers__get():
        response_body, status_code = travelers_request_handler.travelers_get_all_handler(dict(request.args))
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=["GET"])
    def api_traveler_id__get(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_get_handler(traveler_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=["DELETE"])
    def api_traveler_id__delete(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_delete_handler(traveler_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>", methods=["PATCH"])
    def api_traveler_id__patch(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_patch_handler(traveler_id, request.json)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/traveler/<traveler_id>/timeline", methods=["GET"])
    def api_traveler_id_timeline__get(traveler_id: str):
        response_body, status_code = travelers_request_handler.traveler_timeline_get_handler(traveler_id)
        return jsonify(response_body), status_code
