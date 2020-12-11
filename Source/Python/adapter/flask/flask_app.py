from json import loads
from pathlib import Path

from ruamel.yaml import load, YAML
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from adapter.flask.flask_controllers import register_locations_routes, register_travelers_routes
from adapter.main import TimelineTrackerApp


def _create_flask_web_app() -> Flask:
    # File Paths
    _PROJECT_ROOT = Path(__file__).parents[4]
    _RESOURCE_FOLDER = _PROJECT_ROOT.joinpath("Source", "Resources")

    # Web Paths
    _SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
    _API_SPECIFICATION_URL = '/static/apiSpecification.json'  # Our API url (can of course be a local resource)

    # Construct Flask web service
    flask_web_app = Flask(
        __name__,
        root_path=_RESOURCE_FOLDER.joinpath("FlaskWebAppRoot").as_posix(),
        static_folder=_RESOURCE_FOLDER.joinpath("StaticallyServedFiles").as_posix(),
        static_url_path="/static",
    )

    # Call flask_swagger_ui blueprint factory function
    swagger_ui_blueprint = get_swaggerui_blueprint(
        _SWAGGER_URL,
        _API_SPECIFICATION_URL,
    )

    # Register blueprint at URL
    # (URL must match the one given to factory function above)
    flask_web_app.register_blueprint(swagger_ui_blueprint, url_prefix=_SWAGGER_URL)

    # Setup web path root
    @flask_web_app.route('/')
    def web_root():
        return 'It Works!  <a href="/api/docs"> API </a>'

    return flask_web_app


def run_app(*, timeline_tracker_app_config: dict, flask_run_config: dict):
    flask_web_app = _create_flask_web_app()
    timeline_tracker_application = TimelineTrackerApp(**timeline_tracker_app_config)
    register_locations_routes(flask_web_app, timeline_tracker_application.locations_request_handler)
    register_travelers_routes(flask_web_app, timeline_tracker_application.travelers_request_handler)

    flask_web_app.run(**flask_run_config)


if __name__ == '__main__':
    import sys
    config_file = sys.argv[1]
    config: dict = YAML(typ="safe").load(Path(config_file))
    run_app(**config)
