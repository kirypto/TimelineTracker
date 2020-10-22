from flask import request, Flask, jsonify

from adapter.main import TimelineTrackerApp


def register_locations_routes(flask_web_app: Flask, application: TimelineTrackerApp):
    @flask_web_app.route("/api/location", methods=["POST"])
    def api_location():
        response_body, status_code = application.locations_request_handler.locations_post_handler(request_body=request.json)
        return jsonify(response_body), status_code
