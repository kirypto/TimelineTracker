from random import choices, uniform, randint, choice
from string import ascii_letters, printable, digits, ascii_lowercase
from typing import Type, Any, Set, List, TypeVar
from uuid import uuid4

from domain.collections import Range
from domain.events import Event
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.positions import Position, PositionalRange, MovementType, PositionalMove
from domain.tags import Tag, TaggedEntity
from domain.travelers import Traveler


_T = TypeVar("_T")


def _coalesce(obj: _T, fallback: _T) -> _T:
    return obj if obj is not None else fallback


def anon_anything(*, not_type: Type = None) -> Any:
    random_items = [
        False,
        True,
        anon_name(),
        anon_tag(),
        anon_int(),
        anon_float(),
        anon_prefixed_id()
    ]
    return choice([item for item in random_items if type(item) is not not_type])


def anon_description(num_chars: int = 100) -> str:
    return "".join(choices(printable, k=num_chars))


def anon_float(a: float = None, b: float = None) -> float:
    start = a if a is not None else -999999.9
    end = b if b is not None else 999999.9
    return uniform(start, end)


def anon_id_prefix(num_digits: int = 10) -> str:
    return "".join(choices(ascii_letters + "_", k=num_digits))


def anon_identified_entity() -> IdentifiedEntity:
    return IdentifiedEntity(id=anon_prefixed_id())


def anon_int(a: int = None, b: int = None) -> int:
    start = a if a is not None else -999999
    end = b if b is not None else 999999
    return randint(start, end)


def anon_journey() -> List[PositionalMove]:
    return [PositionalMove(position=anon_position(), movement_type=MovementType.IMMEDIATE) for _ in range(5)]


def anon_movement_type() -> MovementType:
    return choice([t for t in MovementType])


def anon_name(num_chars: int = 10) -> str:
    return ("".join(choices(ascii_letters + "_. ", k=num_chars))).strip()


def anon_prefixed_id(*, prefix: str = None) -> PrefixedUUID:
    return PrefixedUUID(_coalesce(prefix, anon_id_prefix(20)), uuid4())


def anon_position(continuum: float = None, reality: int = None) -> Position:
    return Position(latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), continuum=_coalesce(continuum, anon_float()),
                    reality=_coalesce(reality, anon_int()))


def anon_positional_move(*, movement_type: MovementType = None) -> PositionalMove:
    return PositionalMove(position=anon_position(), movement_type=_coalesce(movement_type, anon_movement_type()))


def anon_range(*, whole_numbers: bool = False) -> Range:
    low = anon_float()
    high = low + abs(anon_float())
    if whole_numbers:
        low = float(int(low))
        high = float(int(low))
    return Range(low=low, high=high)


def anon_positional_range(*, continuum: Range[float] = None) -> PositionalRange:
    return PositionalRange(
        latitude=(anon_range()),
        longitude=(anon_range()),
        altitude=(anon_range()),
        continuum=_coalesce(continuum, anon_range()),
        reality=(anon_range(whole_numbers=True)))


def anon_location(*, id: PrefixedUUID = None, name: str = None, tags: Set[Tag] = None, span: PositionalRange = None) -> Location:
    return Location(id=_coalesce(id, anon_prefixed_id(prefix="location")),
                    span=_coalesce(span, anon_positional_range()),
                    name=_coalesce(name, anon_name()),
                    description=anon_description(),
                    tags=_coalesce(tags, {anon_tag()}))


def anon_tag() -> Tag:
    return Tag(anon_tag_name())


def anon_tag_name(num_digits: int = 10) -> str:
    return "".join(choices(ascii_lowercase + digits + "-_", k=num_digits))


def anon_tagged_entity(num_tags: int = 3) -> TaggedEntity:
    tags = {anon_tag() for _ in range(num_tags)}
    return TaggedEntity(tags=tags)


def anon_traveler(*, name: str = None, tags: Set[Tag] = None, journey: List[PositionalMove] = None) -> Traveler:
    return Traveler(id=anon_prefixed_id(prefix="traveler"),
                    name=_coalesce(name, anon_name()),
                    description=anon_description(),
                    journey=_coalesce(journey, anon_journey()),
                    tags=_coalesce(tags, {anon_tag()}))


def anon_event(*, affected_locations: Set[PrefixedUUID] = None, affected_travelers: Set[PrefixedUUID] = None, span: PositionalRange = None) -> Event:
    return Event(
        affected_locations=_coalesce(affected_locations, set()),
        affected_travelers=_coalesce(affected_travelers, set()),
        id=anon_prefixed_id(prefix="event"), name=anon_name(), description=anon_description(),
        span=_coalesce(span, anon_positional_range()),
        tags={anon_tag()})


def anon_create_location_kwargs(*, name: str = None, description: str = None, span: PositionalRange = None, tags: Set[Tag] = None) -> dict:
    return {
        "name": _coalesce(name, anon_name()),
        "description": _coalesce(description, anon_description()),
        "span": _coalesce(span, anon_positional_range()),
        "tags": _coalesce(tags, {anon_tag()}),
    }


def anon_create_traveler_kwargs(
        *, name: str = None, description: str = None, journey: List[PositionalMove] = None, tags: Set[Tag] = None) -> dict:
    return {
        "name": _coalesce(name, anon_name()),
        "description": _coalesce(description, anon_description()),
        "journey": _coalesce(journey, anon_journey()),
        "tags": _coalesce(tags, {anon_tag()}),
    }


def anon_create_event_kwargs(
        *, name: str = None, description: str = None, span: PositionalRange = None, tags: Set[Tag] = None,
        affected_locations: Set[PrefixedUUID] = None, affected_travelers: Set[PrefixedUUID] = None) -> dict:
    return {
        "name": _coalesce(name, anon_name()),
        "description": _coalesce(description, anon_description()),
        "span": _coalesce(span, anon_positional_range()),
        "tags": _coalesce(tags, {anon_tag()}),
        "affected_locations": _coalesce(affected_locations, set()),
        "affected_travelers": _coalesce(affected_travelers, set()),
    }
