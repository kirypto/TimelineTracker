from flask import request, Flask, jsonify

from adapter.main import TimelineTrackerApp


def register_locations_routes(flask_web_app: Flask, application: TimelineTrackerApp):
    @flask_web_app.route("/api/location", methods=["POST"])
    def api_location__post():
        response_body, status_code = application.locations_request_handler.locations_post_handler(request.json)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/locations", methods=["GET"])
    def api_locations__get():
        response_body, status_code = application.locations_request_handler.locations_get_all_handler(dict(request.args))
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["GET"])
    def api_location_id__get(location_id: str):
        response_body, status_code = application.locations_request_handler.location_get_handler(location_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["DELETE"])
    def api_location_id__delete(location_id: str):
        response_body, status_code = application.locations_request_handler.location_delete_handler(location_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>", methods=["PATCH"])
    def api_location_id__patch(location_id: str):
        response_body, status_code = application.locations_request_handler.location_patch_handler(location_id)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/location/<location_id>/timeline", methods=["GET"])
    def api_location_id_timeline__get(location_id: str):
        response_body, status_code = application.locations_request_handler.location_timeline_get_handler(location_id)
        return jsonify(response_body), status_code
