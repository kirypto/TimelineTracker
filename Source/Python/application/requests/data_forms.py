from math import isinf
from typing import Any, Set, List, Generic, TypeVar, Type, Union, Dict
from uuid import UUID

from domain.collections import Range
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.positions import PositionalRange, PositionalMove, Position, MovementType
from domain.tags import Tag
from domain.travelers import Traveler
from domain.worlds import World


T = TypeVar("T")


def _translate_reality_to_json(reality: Union[Range[float], float]) -> Any:
    if type(reality) is float:
        return reality if isinf(reality) else int(reality)
    else:
        return {
            "low": _translate_reality_to_json(reality.low),
            "high": _translate_reality_to_json(reality.high),
        }


class JsonTranslator(Generic[T]):
    __pass_through_types = [int, float, bool]
    __to_str_types = [PrefixedUUID, Tag]

    @staticmethod
    def to_json(value: T) -> Any:
        if type(value) in JsonTranslator.__pass_through_types:
            return value
        if type(value) in JsonTranslator.__to_str_types:
            return str(value)
        if type(value) is str:
            return value
        if type(value) is list:
            return [JsonTranslator.to_json(inner_val) for inner_val in value]
        if type(value) is set:
            return sorted([JsonTranslator.to_json(inner_val) for inner_val in value])
        if type(value) is MovementType:
            movement_type: MovementType = value
            return movement_type.value
        if type(value) is dict:
            return {
                JsonTranslator.to_json(key): JsonTranslator.to_json(val)
                for key, val in value.items()
            }
        if type(value) in {World, Location, Event, Traveler, PositionalRange, Position, Range, PositionalMove}:
            return {
                str(key).removeprefix("_"): JsonTranslator.to_json(val)
                for key, val in vars(value).items()
            }
        raise TypeError(f"Unsupported type {type(value)}")

    @staticmethod
    def from_json(value: Any, type_: Type[T]) -> T:
        try:
            if type_ in JsonTranslator.__pass_through_types:
                return type_(value)
            if type_ is str:
                if type(value) is not str:
                    raise ValueError(f"Expected a str, got {type(value)}")
                return value
            if type_ is Set[PrefixedUUID]:
                ids_json: list = value
                return {JsonTranslator.from_json(id_, PrefixedUUID) for id_ in ids_json}
            if type_ is PrefixedUUID:
                prefixed_uuid_raw: str = value
                prefix, uuid = prefixed_uuid_raw.split("-", 1)
                return PrefixedUUID(prefix, UUID(uuid))
            if type_ is PositionalRange:
                positional_range_json: dict = value
                return PositionalRange(**{
                    "latitude": JsonTranslator.from_json(positional_range_json["latitude"], Range[float]),
                    "longitude": JsonTranslator.from_json(positional_range_json["longitude"], Range[float]),
                    "altitude": JsonTranslator.from_json(positional_range_json["altitude"], Range[float]),
                    "continuum": JsonTranslator.from_json(positional_range_json["continuum"], Range[float]),
                    "reality": JsonTranslator.from_json(positional_range_json["reality"], Set[int]),
                })
            if type_ is Range[float]:
                if type(value) in {int, float}:
                    value = {"low": value, "high": value}
                range_json: dict = value
                return Range(**{
                    "low": JsonTranslator.from_json(range_json["low"], float),
                    "high": JsonTranslator.from_json(range_json["high"], float),
                })
            if type_ is Set[Tag]:
                tags_json: list = value
                return {JsonTranslator.from_json(tag, Tag) for tag in tags_json}
            if type_ is Tag:
                tag_raw: str = value
                return Tag(tag_raw.lower())
            if type_ is List[PositionalMove]:
                movements_json: list = value
                return [JsonTranslator.from_json(move, PositionalMove) for move in movements_json]
            if type_ is PositionalMove:
                positional_movement_json: dict = value
                return PositionalMove(**{
                    "position": JsonTranslator.from_json(positional_movement_json["position"], Position),
                    "movement_type": JsonTranslator.from_json(positional_movement_json["movement_type"], MovementType),
                })
            if type_ is Position:
                position_json: dict = value
                return Position(**{
                    "latitude": JsonTranslator.from_json(position_json["latitude"], float),
                    "longitude": JsonTranslator.from_json(position_json["longitude"], float),
                    "altitude": JsonTranslator.from_json(position_json["altitude"], float),
                    "continuum": JsonTranslator.from_json(position_json["continuum"], float),
                    "reality": JsonTranslator.from_json(position_json["reality"], float),
                })
            if type_ is MovementType:
                movement_type_raw: str = value
                return MovementType(movement_type_raw)
            if type_ is Dict[str, str]:
                string_dict: Dict[str, str] = value
                return {
                    JsonTranslator.from_json(key, str): JsonTranslator.from_json(val, str)
                    for key, val in string_dict.items()
                }
            if type_ is Location:
                location_json: dict = value
                return Location(**{
                    "id": JsonTranslator.from_json(location_json["id"], PrefixedUUID),
                    "name": JsonTranslator.from_json(location_json["name"], str),
                    "description": JsonTranslator.from_json(location_json["description"], str),
                    "span": JsonTranslator.from_json(location_json["span"], PositionalRange),
                    "tags": JsonTranslator.from_json(location_json["tags"], Set[Tag]),
                    "attributes": JsonTranslator.from_json(location_json["attributes"], Dict[str, str]),
                })
            if type_ is Traveler:
                traveler_json: dict = value
                return Traveler(**{
                    "id": JsonTranslator.from_json(traveler_json["id"], PrefixedUUID),
                    "name": JsonTranslator.from_json(traveler_json["name"], str),
                    "description": JsonTranslator.from_json(traveler_json["description"], str),
                    "journey": JsonTranslator.from_json(traveler_json["journey"], List[PositionalMove]),
                    "tags": JsonTranslator.from_json(traveler_json["tags"], Set[Tag]),
                    "attributes": JsonTranslator.from_json(traveler_json["attributes"], Dict[str, str]),
                })
            if type_ is Event:
                event_json: dict = value
                return Event(**{
                    "id": JsonTranslator.from_json(event_json["id"], PrefixedUUID),
                    "name": JsonTranslator.from_json(event_json["name"], str),
                    "description": JsonTranslator.from_json(event_json["description"], str),
                    "span": JsonTranslator.from_json(event_json["span"], PositionalRange),
                    "tags": JsonTranslator.from_json(event_json["tags"], Set[Tag]),
                    "attributes": JsonTranslator.from_json(event_json["attributes"], Dict[str, str]),
                    "affected_locations": JsonTranslator.from_json(event_json["affected_locations"], Set[PrefixedUUID]),
                    "affected_travelers": JsonTranslator.from_json(event_json["affected_travelers"], Set[PrefixedUUID]),
                })
            if type_ is Set[int]:
                ints_json: list = value
                return {JsonTranslator.from_json(integer, int) for integer in ints_json}
        except BaseException as e:
            if type(type_) is type:
                name = type_.__name__
            else:
                name = str(type_).split(".")[-1]
            raise type(e)(f"Error when parsing {name}: {e}")
        raise TypeError(f"Unsupported type {type_}")
