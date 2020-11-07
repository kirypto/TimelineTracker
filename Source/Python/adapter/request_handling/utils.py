from typing import Union, Tuple


def error_response(message: Union[str, BaseException], status_code: int) -> Tuple[dict, int]:
    return {"error": str(message)}, status_code
