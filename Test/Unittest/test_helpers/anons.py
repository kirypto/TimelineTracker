from random import choices, uniform, randint
from string import ascii_letters, printable, digits
from uuid import uuid4

from domain.collections import Range
from domain.ids import PrefixedUUID, IdentifiedEntity
from domain.locations import Location
from domain.positions import Position, PositionalRange
from domain.tags import Tag, TaggedEntity


def anon_description(num_chars: int = 100) -> str:
    return "".join(choices(printable, k=num_chars))


def anon_float(a: float = None, b: float = None):
    start = a if a is not None else -999999.9
    end = b if b is not None else 999999.9
    return uniform(start, end)


def anon_id_prefix(num_digits: int = 10) -> str:
    return "".join(choices(ascii_letters + "_", k=num_digits))


def anon_identified_entity() -> IdentifiedEntity:
    return IdentifiedEntity(id=anon_prefixed_id())


def anon_int(a: int = None, b: int = None):
    start = a if a is not None else -999999
    end = b if b is not None else 999999
    return randint(start, end)


def anon_location() -> Location:
    return Location(id=PrefixedUUID(prefix="location", uuid=uuid4()),
                    span=anon_positional_range(),
                    name=anon_name(),
                    description=anon_description(),
                    tags={anon_tag()})


def anon_name(num_chars: int = 10) -> str:
    return "".join(choices(ascii_letters + "_ ", k=num_chars))


def anon_prefixed_id() -> PrefixedUUID:
    return PrefixedUUID(anon_id_prefix(20), uuid4())


def anon_position() -> Position:
    return Position(latitude=anon_float(), longitude=anon_float(), altitude=anon_float(), continuum=anon_float(), reality=anon_int())


def anon_positional_range() -> PositionalRange:
    return PositionalRange(latitude=(anon_range()), longitude=(anon_range()), altitude=(anon_range()), continuum=(anon_range()),
                           reality=(anon_range(int)))


def anon_range(of_type: type = float):
    if of_type is float:
        low = anon_float()
        high = low + abs(anon_float())
    elif of_type is int:
        low = anon_int()
        high = low + abs(anon_int())
    else:
        raise ValueError(f"Type {type} is not supported")
    return Range(low=low, high=high)


def anon_tag() -> Tag:
    return Tag(anon_tag_name())


def anon_tag_name(num_digits: int = 10) -> str:
    return "".join(choices(ascii_letters + digits + "-_", k=num_digits))


def anon_tagged_entity(num_tags: int = 3) -> TaggedEntity:
    tags = {anon_tag() for _ in range(num_tags)}
    return TaggedEntity(tags=tags)