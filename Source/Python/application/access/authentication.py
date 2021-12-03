from functools import wraps
from logging import error, info
from typing import Callable

from application.access.clients import Profile
from application.access.errors import AuthError


def requires_authentication(*, profile_pass_through: bool = False) -> Callable:
    def wrapper(function: Callable) -> Callable:
        @wraps(function)
        def decorated(*args, profile: Profile = None, **kwargs):
            if profile is None:
                info(f"Declined access to resource {function.__qualname__}, no profile provided.")
                raise AuthError("Insufficient authentication for this resource.")

            elif not isinstance(profile, Profile):
                error(f"Argument profile is of invalid type, was {type(profile)}")
                raise TypeError(f"Argument profile is of invalid type.")

            else:
                info(f"Authenticated {profile.name} for access to {function.__qualname__}")

            if profile_pass_through:
                kwargs["profile"] = profile
            return function(*args, **kwargs)
        return decorated
    return wrapper
