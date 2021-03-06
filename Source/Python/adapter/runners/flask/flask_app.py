from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from ruamel.yaml import YAML

from adapter.runners.flask.flask_controllers import register_locations_routes, register_travelers_routes, register_events_routes
from application.main import TimelineTrackerApp


def _create_flask_web_app(resource_folder: Path, version: str) -> Flask:
    # Web Paths
    _STATIC_URL_PREFIX = "/static"
    _SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
    _API_SPECIFICATION_URL = f"{_STATIC_URL_PREFIX}/apiSpecification.json"  # Our API url (can of course be a local resource)

    statically_served_files_folder = resource_folder.joinpath("StaticallyServedFiles").as_posix()
    # Construct Flask web service
    flask_web_app = Flask(__name__, static_folder=statically_served_files_folder, static_url_path=_STATIC_URL_PREFIX)

    # Call flask_swagger_ui blueprint factory function
    swagger_ui_blueprint = get_swaggerui_blueprint(
        _SWAGGER_URL,
        _API_SPECIFICATION_URL,
    )

    # Register blueprint at URL
    # (URL must match the one given to factory function above)
    flask_web_app.register_blueprint(swagger_ui_blueprint, url_prefix=_SWAGGER_URL)

    # Setup web path root
    @flask_web_app.route("/")
    def web_root():
        return f"It Works!  <a href=\"/api/docs\"> API {version} </a>"

    return flask_web_app


def _run_app(*, timeline_tracker_app_config: dict, flask_run_config: dict, flask_cors_config: dict) -> None:
    timeline_tracker_flask_app = _create_timeline_tracker_flask_app(timeline_tracker_app_config)
    CORS(timeline_tracker_flask_app, **flask_cors_config)

    timeline_tracker_flask_app.run(**flask_run_config)


def _create_timeline_tracker_flask_app(timeline_tracker_app_config: dict) -> Flask:
    timeline_tracker_app_config["request_handlers_config"] = {
        "request_handler_type": "rest"
    }
    timeline_tracker_application = TimelineTrackerApp(**timeline_tracker_app_config)

    flask_web_app = _create_flask_web_app(timeline_tracker_application.resources_folder, timeline_tracker_application.version)
    register_locations_routes(flask_web_app, timeline_tracker_application.locations_request_handler)
    register_travelers_routes(flask_web_app, timeline_tracker_application.travelers_request_handler)
    register_events_routes(flask_web_app, timeline_tracker_application.event_request_handler)

    return flask_web_app


if __name__ == "__main__":
    import sys
    config_file = sys.argv[1]
    config: dict = YAML(typ="safe").load(Path(config_file))
    _run_app(**config)
