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
        if not id.prefix == "world":
            raise ValueError(f"{World.__name__}'s 'id' must be prefixed with 'world'")
