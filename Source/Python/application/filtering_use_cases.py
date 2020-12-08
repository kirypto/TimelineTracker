from typing import Set, Tuple, TypeVar

from domain.descriptors import NamedEntity
from domain.tags import TaggedEntity, Tag


T_NE = TypeVar("T_NE", bound=NamedEntity)
T_TE = TypeVar("T_TE", bound=TaggedEntity)


class FilteringUseCase:
    @staticmethod
    def filter_named_entities(named_entities: Set[T_NE], *, name_is: str = None, name_has: str = None, **kwargs
                              ) -> Tuple[Set[T_NE], dict]:
        def matches_filters(entity: T_NE) -> bool:
            if name_is is not None and name_is != entity.name:
                return False
            if name_has is not None and name_has not in entity.name:
                return False
            return True

        return {entity for entity in named_entities if matches_filters(entity)}, kwargs

    @staticmethod
    def filter_tagged_entities(tagged_entities: Set[T_TE], *,
                               tagged_all: Set[Tag] = None,
                               tagged_any: Set[Tag] = None,
                               tagged_only: Set[Tag] = None,
                               tagged_none: Set[Tag] = None, **kwargs) -> Tuple[Set[T_TE], dict]:
        def matches_filters(entity: T_TE) -> bool:
            if tagged_all is not None and not tagged_all.issubset(entity.tags):
                return False
            if tagged_any is not None and not tagged_any.intersection(entity.tags):
                return False
            if tagged_only is not None and not tagged_only.issuperset(entity.tags):
                return False
            if tagged_none is not None and not tagged_none.isdisjoint(entity.tags):
                return False
            return True

        return {entity for entity in tagged_entities if matches_filters(entity)}, kwargs
