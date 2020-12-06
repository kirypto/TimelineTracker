from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


class Location(IdentifiedEntity, NamedEntity, DescribedEntity, SpanningEntity, TaggedEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs:
            id: PrefixedUUID = kwargs["id"]
            if not id.prefix == "location":
                raise ValueError("id must begin with 'location'")
        super().__init__(**kwargs)
