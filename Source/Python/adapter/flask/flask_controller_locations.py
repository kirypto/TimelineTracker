from flask import request, Flask, jsonify

from adapter.main import TimelineTrackerApp


def register_locations_routes(flask_web_app: Flask, application: TimelineTrackerApp):
    @flask_web_app.route("/api/location", methods=["POST"])
    def api_location():
        response_body, status_code = application.locations_request_handler.locations_post_handler(request_body=request.json)
        return jsonify(response_body), status_code

    @flask_web_app.route("/api/locations", methods=["GET"])
    def api_locations():
        response_body, status_code = application.locations_request_handler.locations_get_all_handler()
        return jsonify(response_body), status_code
