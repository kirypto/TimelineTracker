from functools import wraps
from typing import Callable
from logging import warning

from application.access.clients import Profile
from application.access.errors import AuthError


def requires_authentication(*, profile_pass_through: bool = False) -> Callable:
    def wrapper(function: Callable) -> Callable:
        @wraps(function)
        def decorated(*args, profile: Profile = None, **kwargs):
            if profile is None:
                # TODO #97 kirypto 2021-11-24: Raise the AuthError instead of logging error
                error = AuthError("Insufficient authentication for this resource.")
                warning("In the future, authentication will be required for this resource.", exc_info=error)
            if profile_pass_through:
                kwargs["profile"] = profile
            return function(*args, **kwargs)
        return decorated
    return wrapper
