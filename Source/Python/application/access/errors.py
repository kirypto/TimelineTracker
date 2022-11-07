class AuthError(RuntimeError):
    _message: str

    @property
    def message(self) -> str:
        return self._message

    def __init__(self, message: str) -> None:
        self._message = message
