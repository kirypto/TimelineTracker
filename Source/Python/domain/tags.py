from functools import total_ordering

from re import match
from typing import Set

from domain.base_entity import BaseEntity


@total_ordering
class Tag:
    _tag: str

    def __init__(self, tag: str) -> None:
        if not isinstance(tag, str) or not match(r"^[a-zA-Z0-9_-]+$", tag):
            raise ValueError(f"Invalid tag name '{tag}'")
        self._tag = tag

    def __str__(self) -> str:
        return self._tag

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._tag)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self._tag == other._tag

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self._tag < other._tag

    def __hash__(self) -> int:
        return hash((self.__class__, self._tag))


class TaggedEntity(BaseEntity):
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaggedEntity):
            return False
        return self._tags == other._tags and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((self.__class__, frozenset(self._tags), super().__hash__()))
