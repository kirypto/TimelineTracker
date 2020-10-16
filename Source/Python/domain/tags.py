from functools import total_ordering

from re import compile, match
from typing import Set


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


class TaggedEntity:
    _tags: Set[Tag]

    def __init__(self, *, tags: Set[Tag] = None, **kwargs) -> None:
        if tags is not None:
            if not isinstance(tags, set) or any([not isinstance(t, Tag) for t in tags]):
                raise ValueError("tags must be a set of Tags")
            self._tags = set(tags)
        else:
            self._tags = set()
        super().__init__(**kwargs)

    @property
    def tags(self) -> Set[Tag]:
        return set(self._tags)

    def add_tag(self, tag: Tag) -> None:
        self._tags.add(tag)

    def remove_tag(self, tag: Tag) -> None:
        self._tags.remove(tag)
