
class Profile:
    _user_id: str
    _name: str

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, user_id: str, name: str) -> None:
        self._user_id = user_id
        self._name = name

    def __eq__(self, other) -> bool:
        if not isinstance(other, Profile):
            return NotImplemented
        return self._user_id == other._user_id

    def __hash__(self) -> int:
        return hash((self.__class__, self._user_id))
