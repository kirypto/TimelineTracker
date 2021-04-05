from typing import Set, Tuple, TypeVar, List

from domain.descriptors import NamedEntity
from domain.positions import Position, PositionalRange, SpanningEntity, JourneyingEntity, PositionalMove
from domain.tags import TaggedEntity, Tag


T_NE = TypeVar("T_NE", bound=NamedEntity)
T_TE = TypeVar("T_TE", bound=TaggedEntity)
T_SE = TypeVar("T_SE", bound=SpanningEntity)
T_JE = TypeVar("T_JE", bound=JourneyingEntity)


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

    @staticmethod
    def filter_spanning_entities(spanning_entities: Set[T_SE], *, span_includes: Position = None, span_intersects: PositionalRange = None, **kwargs
                                 ) -> Tuple[Set[T_SE], dict]:
        def matches_filters(entity: T_SE) -> bool:
            entity_span: PositionalRange = entity.span
            if span_includes is not None and not entity_span.includes(span_includes):
                return False
            if span_intersects is not None and not entity_span.intersects(span_intersects):
                return False
            return True

        return {entity for entity in spanning_entities if matches_filters(entity)}, kwargs

    @staticmethod
    def filter_journeying_entities(journeying_entities: Set[T_JE], *, journey_includes: Position = None, journey_intersects: PositionalRange = None,
                                   **kwargs) -> Tuple[Set[T_SE], dict]:
        def matches_filters(entity: T_JE) -> bool:
            entity_journey: List[PositionalMove] = entity.journey
            if journey_includes is not None and not any(positional_move.position == journey_includes for positional_move in entity_journey):
                return False
            if journey_intersects is not None and \
                    not any(journey_intersects.includes(positional_move.position) for positional_move in entity_journey):
                return False
            return True

        return {entity for entity in journeying_entities if matches_filters(entity)}, kwargs
        pass
