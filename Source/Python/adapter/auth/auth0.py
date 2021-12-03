"""
An Auth0 adapter for a web application.

Currently supports only Flask, but is designed to be extendable to django or other web apps supported by authlib. Because of this, imports
do not occur at the top of the module to prevent ModuleNotFoundErrors. Instead, imports are made within scope of the methods needing them.
"""
from functools import wraps
from logging import info
from typing import Any, Callable
from urllib.parse import urlencode

from application.access.clients import Profile


def setup_flask_auth(
        _flask_web_app: Any, login_route: str, login_return_route: str, logout_route: str,
        logout_return_route: str, *, auth_callback_route: str, client_id: str, **auth0_config
) -> None:
    from flask import Flask, session, redirect, request
    from authlib.integrations.flask_client import OAuth
    if not isinstance(_flask_web_app, Flask):
        raise TypeError(f"Cannot setup auth0 for flask: provided web app must be a Flask object but was {type(_flask_web_app)}.")

    info(f"Setting up authorization for web app with: auth_callback_route={auth_callback_route}, login_route={login_route}, "
         f"login_return_route={login_return_route}, logout_route={logout_route}, logout_return_route={logout_return_route}")

    flask_web_app: Flask = _flask_web_app

    oauth = OAuth(flask_web_app)

    auth0 = oauth.register(
        "auth0",
        client_id=client_id,
        **auth0_config,
    )

    @flask_web_app.route(auth_callback_route)
    def callback_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get("userinfo")
        userinfo = resp.json()

        # Store the user information in flask session.
        session["jwt_payload"] = userinfo
        session["profile"] = {
            "user_id": userinfo["sub"],
            "name": userinfo["name"],
            "picture": userinfo["picture"]
        }
        return redirect(login_return_route)

    @flask_web_app.route(login_route)
    def login():
        host_url_without_slash = request.host_url.removesuffix("/")
        return auth0.authorize_redirect(redirect_uri=f"{host_url_without_slash}{auth_callback_route}")

    @flask_web_app.route(logout_route)
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        host_url_without_slash = request.host_url.removesuffix("/")
        params = {"returnTo": f"{host_url_without_slash}{logout_return_route}", "client_id": client_id}
        return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))


def extract_profile_from_flask_session(function: Callable) -> Callable:
    from flask import session

    @wraps(function)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            return function(*args, profile=None, **kwargs)
        profile = Profile(session["profile"]["user_id"], session["profile"]["name"])
        return function(*args, profile=profile, **kwargs)

    return decorated
