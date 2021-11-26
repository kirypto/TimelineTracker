from functools import wraps
from typing import Callable
from logging import warning, error, info

from application.access.clients import Profile
from application.access.errors import AuthError


def requires_authentication(*, profile_pass_through: bool = False) -> Callable:
    def wrapper(function: Callable) -> Callable:
        @wraps(function)
        def decorated(*args, profile: Profile = None, **kwargs):
            if profile is None:
                # TODO #97 kirypto 2021-11-24: Raise the AuthError instead of logging error
                error_message = AuthError("Insufficient authentication for this resource.")
                warning("In the future, authentication will be required for this resource.", exc_info=error_message)
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
