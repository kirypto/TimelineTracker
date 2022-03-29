from random import choices, uniform, randint, choice
from string import ascii_letters, printable, digits, ascii_lowercase
from typing import Type, Any, Set, List, TypeVar, Dict

from application.access.clients import Profile
from domain.collections import Range
from domain.events import Event
from domain.ids import PrefixedUUID, IdentifiedEntity, generate_prefixed_id
from domain.locations import Location
from domain.positions import Position, PositionalRange, MovementType, PositionalMove
from domain.tags import Tag, TaggedEntity
from domain.travelers import Traveler
from domain.worlds import World


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
    return "".join(choices(printable, k=num_chars)).strip() + "\n"


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


def anon_metadata_key() -> str:
    return "".join(choices("_-." + ascii_letters + digits, k=10))


def anon_metadata_value() -> str:
    return "".join(choices(printable, k=50)).strip()


def anon_metadata() -> Dict[str, str]:
    return {
        anon_metadata_key(): anon_metadata_value()
        for _ in range(anon_int(1, 3))
    }


def anon_movement_type() -> MovementType:
    return choice([t for t in MovementType])


def anon_name(num_chars: int = 10) -> str:
    return ("".join(choices(ascii_letters + "_. ", k=num_chars))).strip()


def anon_route(num_chars: int = 10) -> str:
    return "/" + "".join(choices(ascii_letters, k=num_chars))


def anon_string(num_chars: int = 10) -> str:
    return ("".join(choices(printable, k=num_chars))).strip()


def anon_prefixed_id(*, prefix: str = None) -> PrefixedUUID:
    return generate_prefixed_id(_coalesce(prefix, anon_id_prefix(20)))


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
        latitude=anon_range(),
        longitude=anon_range(),
        altitude=anon_range(),
        continuum=_coalesce(continuum, anon_range()),
        reality={anon_int()})


# noinspection PyShadowingBuiltins
def anon_location(
        *, id: PrefixedUUID = None, name: str = None, tags: Set[Tag] = None, span: PositionalRange = None,
        metadata: Dict[str, str] = None) -> Location:
    return Location(
        id=_coalesce(id, anon_prefixed_id(prefix="location")),
        span=_coalesce(span, anon_positional_range()),
        name=_coalesce(name, anon_name()),
        description=anon_description(),
        tags=_coalesce(tags, {anon_tag()}),
        metadata=_coalesce(metadata, anon_metadata()),
    )


# noinspection PyShadowingBuiltins
def anon_world(*, id: PrefixedUUID = None, name: str = None, tags: Set[Tag] = None, metadata: Dict[str, str] = None) -> World:
    return World(
        id=_coalesce(id, anon_prefixed_id(prefix="world")),
        name=_coalesce(name, anon_name()),
        description=anon_description(),
        tags=_coalesce(tags, {anon_tag()}),
        metadata=_coalesce(metadata, anon_metadata()),
    )


def anon_tag() -> Tag:
    return Tag(anon_tag_name())


def anon_tag_name(num_digits: int = 10) -> str:
    return "".join(choices(ascii_lowercase + digits + "-_", k=num_digits))


def anon_tagged_entity(num_tags: int = 3) -> TaggedEntity:
    tags = {anon_tag() for _ in range(num_tags)}
    return TaggedEntity(tags=tags)


def anon_traveler(*, name: str = None, tags: Set[Tag] = None, journey: List[PositionalMove] = None, metadata: Dict[str, str] = None
                  ) -> Traveler:
    return Traveler(
        id=anon_prefixed_id(prefix="traveler"),
        name=_coalesce(name, anon_name()),
        description=anon_description(),
        journey=_coalesce(journey, anon_journey()),
        tags=_coalesce(tags, {anon_tag()}),
        metadata=_coalesce(metadata, anon_metadata())
    )


def anon_event(
        *, affected_locations: Set[PrefixedUUID] = None, affected_travelers: Set[PrefixedUUID] = None, span: PositionalRange = None,
        metadata: Dict[str, str] = None, tags: Set[Tag] = None) -> Event:
    return Event(
        affected_locations=_coalesce(affected_locations, set()),
        affected_travelers=_coalesce(affected_travelers, set()),
        id=anon_prefixed_id(prefix="event"), name=anon_name(), description=anon_description(),
        span=_coalesce(span, anon_positional_range()),
        tags=_coalesce(tags, {anon_tag()}),
        metadata=_coalesce(metadata, anon_metadata())
    )


def anon_create_location_kwargs(
        *, name: str = None, description: str = None, span: PositionalRange = None, tags: Set[Tag] = None, metadata: Dict[str, str] = None
) -> dict:
    return {
        "name": _coalesce(name, anon_name()),
        "description": _coalesce(description, anon_description()),
        "span": _coalesce(span, anon_positional_range()),
        "tags": _coalesce(tags, {anon_tag()}),
        "metadata": _coalesce(metadata, anon_metadata()),
    }


def anon_create_traveler_kwargs(
        *, name: str = None, description: str = None, journey: List[PositionalMove] = None, tags: Set[Tag] = None,
        metadata: Dict[str, str] = None) -> dict:
    return {
        "name": _coalesce(name, anon_name()),
        "description": _coalesce(description, anon_description()),
        "journey": _coalesce(journey, anon_journey()),
        "tags": _coalesce(tags, {anon_tag()}),
        "metadata": _coalesce(metadata, anon_metadata()),
    }


def anon_create_event_kwargs(
        *, name: str = None, description: str = None, span: PositionalRange = None, tags: Set[Tag] = None,
        affected_locations: Set[PrefixedUUID] = None, affected_travelers: Set[PrefixedUUID] = None, metadata: Dict[str, str] = None
) -> dict:
    return {
        "name": _coalesce(name, anon_name()),
        "description": _coalesce(description, anon_description()),
        "span": _coalesce(span, anon_positional_range()),
        "tags": _coalesce(tags, {anon_tag()}),
        "affected_locations": _coalesce(affected_locations, set()),
        "affected_travelers": _coalesce(affected_travelers, set()),
        "metadata": _coalesce(metadata, anon_metadata()),
    }


def anon_profile() -> Profile:
    return Profile(str(generate_prefixed_id("client")), anon_name())
