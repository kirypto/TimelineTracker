from pathlib import Path

from flask import Flask, redirect
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from ruamel.yaml import YAML
from waitress import serve

from adapter.auth.auth0 import setup_flask_auth, extract_profile_from_flask_session
from adapter.runners.flask.flask_controllers import register_travelers_routes, register_events_routes
from application.access.authentication import requires_authentication
from application.access.clients import Profile
from application.access.errors import AuthError
from application.main import TimelineTrackerApp


def _create_flask_web_app(auth_config: dict, resource_folder: Path, version: str, secret_key: str) -> Flask:
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

    flask_web_app.secret_key = secret_key

    login_route = "/login"
    logout_route = "/logout"
    home_route = "/home"
    dashboard_route = "/dashboard"

    # Setup web path root
    @flask_web_app.route(dashboard_route)
    @extract_profile_from_flask_session
    @requires_authentication(profile_pass_through=True)
    def dashboard_page(profile: Profile):
        return f"""
        <div> Logged in as {profile.name} <div>
        <div> <a href=\"/api/docs\"> API {version} Documentation </a> </div>
        <div> <button onclick="window.location.href='{logout_route}'"> Logout </button> </div>
        """

    @flask_web_app.route(home_route)
    @extract_profile_from_flask_session
    def home_page(profile: Profile = None):
        if profile is not None:
            return redirect(dashboard_route)
        return f"""
        <div> It Works! Login to access Dashboard. </div>
        <div> <button onclick="window.location.href='{login_route}'"> Login </button> </div>
        """

    @flask_web_app.route("/")
    def root_endpoint():
        return redirect(home_route)

    @flask_web_app.errorhandler(RuntimeError)
    def error_page(exception: RuntimeError):
        return f"""
        <h1> {type(exception).__name__} </h1>
        <div> {str(exception)} </div>
        {"<div> Return <a href='/home'>Home</a> to login. </div>" if isinstance(exception, AuthError) else ""}
        """

    setup_flask_auth(flask_web_app, login_route, dashboard_route, logout_route, home_route, **auth_config)

    return flask_web_app


def _run_app(
        *, timeline_tracker_app_config: dict, flask_run_config: dict, flask_cors_config: dict, auth_config: dict, secret_key: str,
) -> None:
    timeline_tracker_flask_app = _create_timeline_tracker_flask_app(timeline_tracker_app_config, auth_config, secret_key)
    CORS(timeline_tracker_flask_app, **flask_cors_config)

    serve(timeline_tracker_flask_app, **flask_run_config)


def _create_timeline_tracker_flask_app(timeline_tracker_app_config: dict, auth_config: dict, secret_key: str) -> Flask:
    timeline_tracker_application = TimelineTrackerApp(**timeline_tracker_app_config)

    flask_web_app = _create_flask_web_app(
        auth_config, timeline_tracker_application.resources_folder, timeline_tracker_application.version, secret_key)

    controller_config = dict(
        rest_controller_config=dict(
            controller_class_path="adapter.runners.flask.flask_controllers.FlaskRESTController",
            flask_web_app=flask_web_app,
        ),
    )
    timeline_tracker_application.initialize_controllers(**controller_config)
    register_travelers_routes(flask_web_app, timeline_tracker_application.travelers_request_handler)
    register_events_routes(flask_web_app, timeline_tracker_application.event_request_handler)

    return flask_web_app


if __name__ == "__main__":
    import sys

    config_file = sys.argv[1]
    config: dict = YAML(typ="safe").load(Path(config_file))
    _run_app(**config)
