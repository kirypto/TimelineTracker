"""
An Auth0 adapter for a web application.

Currently supports only Flask, but is designed to be extendable to django or other web apps supported by authlib. Because of this, imports
do not occur at the top of the module to prevent ModuleNotFoundErrors. Instead, imports are made within scope of the methods needing them.
"""
from functools import wraps
from json import loads
from logging import info
from operator import itemgetter
from re import match
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import urlopen

# noinspection PyPackageRequirements
from jose import jwt  # For some reason PyCharm is not detecting that python-jose has been added to requirements.txt

from application.access.clients import Profile
from application.access.errors import AuthError


__AUTH_0_BEARER_TOKEN_INFO = {}


def setup_flask_auth(
        _flask_web_app: Any, login_route: str, login_return_route: str, logout_route: str, logout_return_route: str,
        *, auth_callback_route: str, client_id: str, domain: str, api_audience: str, algorithms: str, **auth0_config
) -> None:
    from flask import Flask, session, redirect, request
    from authlib.integrations.flask_client import OAuth
    if not isinstance(_flask_web_app, Flask):
        raise TypeError(f"Cannot setup auth0 for flask: provided web app must be a Flask object but was {type(_flask_web_app)}.")

    info(f"Setting up authorization for web app with: auth_callback_route={auth_callback_route}, login_route={login_route}, "
         f"login_return_route={login_return_route}, logout_route={logout_route}, logout_return_route={logout_return_route}")

    __AUTH_0_BEARER_TOKEN_INFO.update({
        "domain": domain,
        "api_audience": api_audience,
        "algorithms": algorithms,
    })

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
    from flask import session, request

    @wraps(function)
    def decorated(*args, **kwargs):
        # Check for auth in bearer token
        if "Authorization" in request.headers:
            auth_token_raw = request.headers.get("Authorization")
            auth_token_match = match(r"^[Bb]earer (.+)$", auth_token_raw)
            if not auth_token_match:
                raise AuthError("Invalid header: Authorization header must start with 'Bearer '.")
            token = auth_token_match.group(1)

            domain, api_audience, algorithms = itemgetter("domain", "api_audience", "algorithms")(__AUTH_0_BEARER_TOKEN_INFO)

            jsonurl = urlopen(f"https://{domain}/.well-known/jwks.json")
            jwks = loads(jsonurl.read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=algorithms,
                        audience=api_audience,
                        issuer=f"https://{domain}/"
                    )
                except jwt.ExpiredSignatureError:
                    raise AuthError("Token is expired")
                except jwt.JWTClaimsError:
                    raise AuthError("Incorrect claims: please check the audience and issuer")
                except Exception:
                    raise AuthError("Unable to parse authentication token.")

                profile = Profile(payload["sub"], payload["name"])
                return function(*args, profile=profile, **kwargs)

        # Check for auth in flask session
        if "profile" in session:
            profile = Profile(session["profile"]["user_id"], session["profile"]["name"])
            return function(*args, profile=profile, **kwargs)

        # No auth, pass through None for profile
        return function(*args, profile=None, **kwargs)

    return decorated
