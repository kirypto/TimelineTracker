from functools import wraps
from typing import Callable

from flask import session

from application.access.clients import Profile


def extract_profile_from_session(function: Callable) -> Callable:
    @wraps(function)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            return function(*args, profile=None, **kwargs)
        profile = Profile(session["profile"]["user_id"], session["profile"]["name"])
        return function(*args, profile=profile, **kwargs)
    return decorated
