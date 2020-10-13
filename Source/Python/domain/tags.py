from functools import total_ordering

from re import compile, match


def special_match(strg, search=compile(r'^[a-zA-Z0-9_-]$').search):
    return not bool(search(strg))


@total_ordering
class Tag:
    _name: str

    def __init__(self, name: str) -> None:
        name_valid = match(r"^[a-zA-Z0-9_-]+$", name)
        if not name_valid:
            raise ValueError(f"Invalid tag name '{name}'")
        self._name = name

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._name)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self._name == other._name

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self._name < other._name

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self._name))


class Tags:
    pass
