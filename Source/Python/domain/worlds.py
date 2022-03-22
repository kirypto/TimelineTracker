from domain.descriptors import DescribedEntity, NamedEntity
from domain.ids import IdentifiedEntity, PrefixedUUID
from domain.metadata import MetadataEntity
from domain.tags import TaggedEntity


class World(IdentifiedEntity, NamedEntity, DescribedEntity, TaggedEntity, MetadataEntity):
    def __init__(self, **kwargs) -> None:
        if "id" in kwargs:
            self.validate_id(kwargs["id"])
        super().__init__(**kwargs)

    # noinspection PyShadowingBuiltins
    @classmethod
    def validate_id(cls, id: PrefixedUUID) -> None:
        if not isinstance(id, PrefixedUUID):
            raise ValueError(f"{World.__name__}'s 'id' attribute must be a {PrefixedUUID.__name__}")
        if not id.prefix == "world":
            raise ValueError(f"{World.__name__}'s 'id' must be prefixed with 'world'")
