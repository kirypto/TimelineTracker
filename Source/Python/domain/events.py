from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.positions import SpanningEntity
from domain.tags import TaggedEntity


class Event(IdentifiedEntity, NamedEntity, DescribedEntity, SpanningEntity, TaggedEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs:
            id: PrefixedUUID = kwargs["id"]
            if not id.prefix == "event":
                raise ValueError("id must begin with 'event'")
        super().__init__(**kwargs)
