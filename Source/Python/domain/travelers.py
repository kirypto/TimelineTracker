from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.positions import JourneyingEntity
from domain.tags import TaggedEntity


class Traveler(IdentifiedEntity, NamedEntity, DescribedEntity, JourneyingEntity, TaggedEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs and isinstance(kwargs["id"], PrefixedUUID):
            id: PrefixedUUID = kwargs["id"]
            if not id.prefix == "traveler":
                raise ValueError("id must begin with 'traveler'")
        super().__init__(**kwargs)
