from typing import Set

from domain.descriptors import NamedEntity
from domain.tags import TaggedEntity, Tag


class FilteringUseCase:
    @staticmethod
    def filter_named_entities(named_entities: Set[NamedEntity], *, name_is: str = None, name_has: str = None) -> Set[NamedEntity]:
        def matches_filters(entity: NamedEntity) -> bool:
            if name_is is not None and name_is != entity.name:
                return False
            if name_has is not None and name_has not in entity.name:
                return False
            return True

        return {entity for entity in named_entities if matches_filters(entity)}

    @staticmethod
    def filter_tagged_entities(tagged_entities: Set[TaggedEntity], *,
                               tagged_all: Set[Tag] = None,
                               tagged_any: Set[Tag] = None,
                               tagged_only: Set[Tag] = None,
                               tagged_none: Set[Tag] = None) -> Set[TaggedEntity]:
        def matches_filters(entity: TaggedEntity) -> bool:
            if tagged_all is not None and not tagged_all.issubset(entity.tags):
                return False
            if tagged_any is not None and not tagged_any.intersection(entity.tags):
                return False
            if tagged_only is not None and not tagged_only.issuperset(entity.tags):
                return False
            if tagged_none is not None and not tagged_none.isdisjoint(entity.tags):
                return False
            return True

        return {entity for entity in tagged_entities if matches_filters(entity)}
