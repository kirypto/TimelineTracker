from collections import defaultdict
from functools import wraps
from pathlib import Path
from typing import Dict, Callable

from flask import Flask, redirect, Response, request, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from ruamel.yaml import YAML
from waitress import serve

from _version import APP_VERSION
from adapter.auth.auth0 import setup_flask_auth, extract_authentication_profile
from application.access.authentication import requires_authentication
from application.access.clients import Profile
from application.access.errors import AuthError
from application.main import TimelineTrackerApp
from application.requests.rest import RESTMethod, MIMEType, RequestHandler, HandlerResult
from application.requests.rest.controllers import RESTController, HandlerRegisterer, validate_route_handler_declaration
from application.requests.rest.utils import with_error_response_on_raised_exceptions


def _create_flask_web_app(auth_config: dict, resource_folder: Path, secret_key: str) -> Flask:
    # Web Paths
    _STATIC_URL_PREFIX = "/static"
    _SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
    _API_SPECIFICATION_URL = f"{_STATIC_URL_PREFIX}/APISpec/apiSpecification.json"  # Our API url (can of course be a local resource)

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
    @extract_authentication_profile
    @requires_authentication(profile_pass_through=True)
    def dashboard_page(profile: Profile):
        return f"""
        <div> Logged in as {profile.name} <div>
        <div> <a href=\"/api/docs\"> API {APP_VERSION} Documentation </a> </div>
        <div> <button onclick="window.location.href='{logout_route}'"> Logout </button> </div>
        """

    @flask_web_app.route(home_route)
    @extract_authentication_profile
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

    flask_web_app = _create_flask_web_app(auth_config, timeline_tracker_application.resources_folder, secret_key)

    controller_config = dict(
        rest_controller_config=dict(
            controller_class_path="adapter.runners.flask_app.FlaskRESTController",
            flask_web_app=flask_web_app,
        ),
    )
    timeline_tracker_application.initialize_controllers(**controller_config)

    return flask_web_app


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
        if method in self._routes[route]:
            # TODO kirypto 2022-Feb24: Ensure tests exist for this
            raise ValueError(f"Cannot register, method {method} already registered for {route}")

        def handler_registerer(handler_func: RequestHandler) -> None:
            validate_route_handler_declaration(route, handler_func, json, query_params)

            def convert_to_flask_response(func: RequestHandler) -> Callable[[...], Response]:
                @wraps(func)
                def wrapper(*args, **kwargs) -> Response:
                    response: HandlerResult = func(*args, **kwargs)
                    status_code, contents = response
                    flask_response = make_response(contents, status_code)
                    flask_response.mimetype = response_type.value
                    return flask_response
                return wrapper

            @convert_to_flask_response
            @with_error_response_on_raised_exceptions
            @extract_authentication_profile
            @wraps(handler_func)
            def handler_wrapper(**kwargs) -> HandlerResult:
                args = []
                if json:
                    if request.json is None:
                        raise ValueError("Json body must be provided")
                    args.append(request.json)
                if query_params:
                    args.append(dict(request.args))

                return handler_func(*args, **kwargs)

            self._routes[route][method] = handler_wrapper

        return handler_registerer

    def finalize(self) -> None:
        if self._finalized:
            raise ValueError("Controller has already been finalized.")

        for route, method_handler_dict in self._routes.items():
            def route_handler(*args, **kwargs):
                request_url = request.url_rule.rule
                rest_method = RESTMethod(request.method.upper())
                return self._routes[request_url][rest_method](*args, **kwargs)

            self._flask_web_app.add_url_rule(route, route, route_handler, methods=[m.value for m in method_handler_dict.keys()])

        self._finalized = True


if __name__ == "__main__":
    import sys

    config_file = sys.argv[1]
    config: dict = YAML(typ="safe").load(Path(config_file))
    _run_app(**config)
