from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.metadata import MetadataEntity
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


class Location(IdentifiedEntity, NamedEntity, DescribedEntity, SpanningEntity, TaggedEntity, MetadataEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs:
            self.validate_id(kwargs["id"])
        super().__init__(**kwargs)

    @classmethod
    def validate_id(cls, id: PrefixedUUID) -> None:
        if not isinstance(id, PrefixedUUID):
            raise ValueError(f"{Location.__name__}'s 'id' attribute must be a {PrefixedUUID.__name__}")
        if not id.prefix == "location":
            raise ValueError(f"{Location.__name__}'s 'id' must be prefixed with 'location'")
