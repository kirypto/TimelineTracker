from uuid import UUID

from domain.attributes import AttributedEntity
from domain.descriptors import DescribedEntity, NamedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.tags import TaggedEntity


class World(IdentifiedEntity, NamedEntity, DescribedEntity, TaggedEntity, AttributedEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs:
            self.validate_id(kwargs["id"])
        super().__init__(**kwargs)

    @classmethod
    def validate_id(cls, id: PrefixedUUID) -> None:
        if not isinstance(id, PrefixedUUID):
            raise ValueError(f"{World.__name__}'s 'id' attribute must be a {PrefixedUUID.__name__}")
        prefix = id.prefix
        _validate_prefix(prefix)


def to_world_id(id: str) -> PrefixedUUID:
    if "-" not in id:
        raise ValueError(f"Invalid {World.__name__} id '{id}'")
    prefix, uuid = id.split("-", maxsplit=1)
    _validate_prefix(prefix)
    return PrefixedUUID(prefix, UUID(uuid))


def _validate_prefix(prefix):
    if not prefix == "world":
        raise ValueError(f"{World.__name__}'s 'id' must be prefixed with 'world'")
