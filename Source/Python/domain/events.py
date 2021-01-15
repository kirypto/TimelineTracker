from typing import Set

from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.metadata import MetadataEntity
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


class Event(IdentifiedEntity, NamedEntity, DescribedEntity, SpanningEntity, TaggedEntity, MetadataEntity):
    _affected_locations: Set[PrefixedUUID]
    _affected_travelers: Set[PrefixedUUID]

    @property
    def affected_locations(self) -> Set[PrefixedUUID]:
        return set(self._affected_locations)

    @property
    def affected_travelers(self) -> Set[PrefixedUUID]:
        return set(self._affected_travelers)

    def __init__(self, *, affected_locations: Set[PrefixedUUID] = frozenset(), affected_travelers: Set[PrefixedUUID] = frozenset(), **kwargs) -> None:
        if "id" in kwargs:
            self.validate_id(kwargs["id"])
        super().__init__(**kwargs)
        self._affected_locations = set(affected_locations)
        self._affected_travelers = set(affected_travelers)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Event):
            return False
        return (self._affected_locations == other._affected_locations
                and self._affected_travelers == other._affected_travelers
                and super().__eq__(other))

    def __hash__(self) -> int:
        return hash((Event, frozenset(self._affected_locations), frozenset(self._affected_travelers), super().__hash__()))

    @classmethod
    def validate_id(cls, id: PrefixedUUID) -> None:
        if not isinstance(id, PrefixedUUID):
            raise ValueError(f"{Event.__name__}'s 'id' attribute must be a {PrefixedUUID.__name__}")
        if not id.prefix == "event":
            raise ValueError(f"{Event.__name__}'s 'id' must be prefixed with 'event'")
