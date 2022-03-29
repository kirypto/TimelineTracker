from domain.descriptors import NamedEntity, DescribedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.metadata import AttributedEntity
from domain.positions import JourneyingEntity
from domain.tags import TaggedEntity


class Traveler(IdentifiedEntity, NamedEntity, DescribedEntity, JourneyingEntity, TaggedEntity, AttributedEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs and isinstance(kwargs["id"], PrefixedUUID):
            self.validate_id(kwargs["id"])
        super().__init__(**kwargs)

    @classmethod
    def validate_id(cls, id: PrefixedUUID) -> None:
        if not isinstance(id, PrefixedUUID):
            raise ValueError(f"{Traveler.__name__}'s 'id' attribute must be a {PrefixedUUID.__name__}")
        if not id.prefix == "traveler":
            raise ValueError(f"{Traveler.__name__}'s 'id' must be prefixed with 'traveler'")
