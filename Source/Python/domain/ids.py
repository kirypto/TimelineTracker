from re import match
from uuid import UUID

from domain.base_entity import BaseEntity


class PrefixedUUID:
    _prefix: str
    _uuid: UUID
    __delimiter: str = "-"

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def uuid(self) -> UUID:
        return self._uuid

    def __init__(self, prefix: str, uuid: UUID) -> None:
        if not isinstance(uuid, UUID):
            raise TypeError(f"Must be {UUID.__name__}")
        if uuid.version != 4:
            raise ValueError(f"Must be version 4")
        if not isinstance(prefix, str) or not match(r"^\w+$", prefix):
            raise ValueError(f"Prefix must contain only alphanumeric and underscore characters")

        self._prefix = prefix
        self._uuid = uuid

    def __str__(self) -> str:
        return f"{self._prefix}{self.__delimiter}{self._uuid}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._prefix)}, {repr(self._uuid)})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, PrefixedUUID):
            return NotImplemented
        return self._prefix == other._prefix and self._uuid == other._uuid

    def __hash__(self) -> int:
        return hash((self.__class__, self._prefix, self._uuid))


class IdentifiedEntity(BaseEntity):
    _id: PrefixedUUID

    @property
    def id(self) -> PrefixedUUID:
        return self._id

    def __init__(self, *, id: PrefixedUUID, **kwargs):
        if not isinstance(id, PrefixedUUID):
            raise TypeError(f"Argument 'id' must be a {PrefixedUUID}")
        self._id = id
        super().__init__(**kwargs)

    def __eq__(self, other) -> bool:
        if not isinstance(other, IdentifiedEntity):
            return False
        return self._id == other._id and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((self.__class__, self._id))
