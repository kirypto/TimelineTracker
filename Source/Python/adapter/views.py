from abc import ABC, abstractmethod
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


T = TypeVar("T")


def _translate_reality_to_json(reality: Union[Range[float], float]) -> Any:
    if type(reality) is float:
        return reality if isinf(reality) else int(reality)
    else:
        return {
            "low": _translate_reality_to_json(reality.low),
            "high": _translate_reality_to_json(reality.high),
        }


class ValueTranslator(Generic[T]):
    __pass_through_types = [int, float, bool]
    __to_str_types = [PrefixedUUID, Tag]

    @staticmethod
    def to_json(value: T) -> Any:
        if type(value) in ValueTranslator.__pass_through_types:
            return value
        if type(value) in ValueTranslator.__to_str_types:
            return str(value)
        if type(value) is str:
            return value
        if type(value) in {set, list}:
            return [ValueTranslator.to_json(inner_val) for inner_val in value]
        if type(value) is MovementType:
            movement_type: MovementType = value
            return movement_type.value
        if type(value) is dict:
            return {
                ValueTranslator.to_json(key): ValueTranslator.to_json(val)
                for key, val in value.items()
            }
        if type(value) in {Location, Event, Traveler, PositionalRange, Position, Range, PositionalMove}:
            location: Location = value
            return {
                str(key).removeprefix("_"): ValueTranslator.to_json(val)
                for key, val in vars(location).items()
            }
        raise TypeError(f"Unsupported type {type(value)}")

    @staticmethod
    def from_json(value: Any, type_: Type[T]) -> T:
        try:
            if type_ in ValueTranslator.__pass_through_types:
                return type_(value)
            if type_ is str:
                if type(value) is not str:
                    raise ValueError(f"Expected a str, got {type(value)}")
                return value
            if type_ is Set[PrefixedUUID]:
                ids_json: list = value
                return {ValueTranslator.from_json(id_, PrefixedUUID) for id_ in ids_json}
            if type_ is PrefixedUUID:
                prefixed_uuid_raw: str = value
                prefix, uuid = prefixed_uuid_raw.split("-", 1)
                return PrefixedUUID(prefix, UUID(uuid))
            if type_ is PositionalRange:
                positional_range_json: dict = value
                return PositionalRange(**{
                    "latitude": ValueTranslator.from_json(positional_range_json["latitude"], Range[float]),
                    "longitude": ValueTranslator.from_json(positional_range_json["longitude"], Range[float]),
                    "altitude": ValueTranslator.from_json(positional_range_json["altitude"], Range[float]),
                    "continuum": ValueTranslator.from_json(positional_range_json["continuum"], Range[float]),
                    "reality": ValueTranslator.from_json(positional_range_json["reality"], Range[float]),
                })
            if type_ is Range[float]:
                range_json: dict = value
                return Range(**{
                    "low": ValueTranslator.from_json(range_json["low"], float),
                    "high": ValueTranslator.from_json(range_json["high"], float),
                })
            if type_ is Set[Tag]:
                tags_json: list = value
                return {ValueTranslator.from_json(tag, Tag) for tag in tags_json}
            if type_ is Tag:
                tag_raw: str = value
                return Tag(tag_raw.lower())
            if type_ is List[PositionalMove]:
                movements_json: list = value
                return [ValueTranslator.from_json(move, PositionalMove) for move in movements_json]
            if type_ is PositionalMove:
                positional_movement_json: dict = value
                return PositionalMove(**{
                    "position": ValueTranslator.from_json(positional_movement_json["position"], Position),
                    "movement_type": ValueTranslator.from_json(positional_movement_json["movement_type"], MovementType),
                })
            if type_ is Position:
                position_json: dict = value
                return Position(**{
                    "latitude": ValueTranslator.from_json(position_json["latitude"], float),
                    "longitude": ValueTranslator.from_json(position_json["longitude"], float),
                    "altitude": ValueTranslator.from_json(position_json["altitude"], float),
                    "continuum": ValueTranslator.from_json(position_json["continuum"], float),
                    "reality": ValueTranslator.from_json(position_json["reality"], float),
                })
            if type_ is MovementType:
                movement_type_raw: str = value
                return MovementType(movement_type_raw)
            if type_ is Dict[str, str]:
                string_dict: Dict[str, str] = value
                return {
                    ValueTranslator.from_json(key, str): ValueTranslator.from_json(val, str)
                    for key, val in string_dict.items()
                }
            if type_ is Location:
                location_json: dict = value
                return Location(**{
                    "id": ValueTranslator.from_json(location_json["id"], PrefixedUUID),
                    "name": ValueTranslator.from_json(location_json["name"], str),
                    "description": ValueTranslator.from_json(location_json["description"], str),
                    "span": ValueTranslator.from_json(location_json["span"], PositionalRange),
                    "tags": ValueTranslator.from_json(location_json["tags"], Set[Tag]),
                    "metadata": ValueTranslator.from_json(location_json["metadata"], Dict[str, str]),
                })
            if type_ is Traveler:
                traveler_json: dict = value
                return Traveler(**{
                    "id": ValueTranslator.from_json(traveler_json["id"], PrefixedUUID),
                    "name": ValueTranslator.from_json(traveler_json["name"], str),
                    "description": ValueTranslator.from_json(traveler_json["description"], str),
                    "journey": ValueTranslator.from_json(traveler_json["journey"], List[PositionalMove]),
                    "tags": ValueTranslator.from_json(traveler_json["tags"], Set[Tag]),
                    "metadata": ValueTranslator.from_json(traveler_json["metadata"], Dict[str, str]),
                })
            if type_ is Event:
                event_json: dict = value
                return Event(**{
                    "id": ValueTranslator.from_json(event_json["id"], PrefixedUUID),
                    "name": ValueTranslator.from_json(event_json["name"], str),
                    "description": ValueTranslator.from_json(event_json["description"], str),
                    "span": ValueTranslator.from_json(event_json["span"], PositionalRange),
                    "tags": ValueTranslator.from_json(event_json["tags"], Set[Tag]),
                    "metadata": ValueTranslator.from_json(event_json["metadata"], Dict[str, str]),
                    "affected_locations": ValueTranslator.from_json(event_json["affected_locations"], Set[PrefixedUUID]),
                    "affected_travelers": ValueTranslator.from_json(event_json["affected_travelers"], Set[PrefixedUUID]),
                })
        except BaseException as e:
            if type(type_) is type:
                name = type_.__name__
            else:
                name = str(type_).split(".")[-1]
            raise type(e)(f"Error when parsing {name}: {e}")
        raise TypeError(f"Unsupported type {type_}")


class _View(ABC):
    @staticmethod
    @abstractmethod
    def to_json(domain_object: Any) -> Any:
        pass


class PrimitiveView(_View, ABC):
    @staticmethod
    @abstractmethod
    def from_json(json_view: Any) -> Any:
        pass


class DomainConstructedView(_View, ABC):
    @staticmethod
    @abstractmethod
    def kwargs_from_json(json_view: Any) -> Any:
        pass


class LocationView(DomainConstructedView):
    __attribute_types_by_name = {
        "id": PrefixedUUID,
        "name": str,
        "description": str,
        "span": PositionalRange,
        "tags": Set[Tag],
        "metadata": Dict[str, str],
    }

    @staticmethod
    def to_json(location: Location) -> dict:
        location_attributes = {attribute_name.replace("_", "", 1): value for attribute_name, value in vars(location).items()}
        return {
            attribute_name: ValueTranslator.to_json(location_attributes[attribute_name])
            for attribute_name in LocationView.__attribute_types_by_name.keys()
        }

    @staticmethod
    def kwargs_from_json(location_view: dict) -> dict:
        def translate_val(attribute_name, value):
            if attribute_name not in LocationView.__attribute_types_by_name:
                raise ValueError(f"Failed to translate attribute '{attribute_name}' when constructing {Location.__name__}")
            return ValueTranslator.from_json(value, LocationView.__attribute_types_by_name[attribute_name])

        return {
            attribute_name: translate_val(attribute_name, value)
            for attribute_name, value in location_view.items()
        }


class TravelerView(DomainConstructedView):
    __attribute_types_by_name = {
        "id": PrefixedUUID,
        "name": str,
        "description": str,
        "journey": List[PositionalMove],
        "tags": Set[Tag],
        "metadata": Dict[str, str],
    }

    @staticmethod
    def to_json(traveler: Traveler) -> dict:
        traveler_attributes = {attribute_name.replace("_", "", 1): value for attribute_name, value in vars(traveler).items()}
        return {
            attribute_name: ValueTranslator.to_json(traveler_attributes[attribute_name])
            for attribute_name in TravelerView.__attribute_types_by_name.keys()
        }

    @staticmethod
    def kwargs_from_json(traveler_view: dict) -> dict:
        def translate_val(attribute_name, value):
            if attribute_name not in TravelerView.__attribute_types_by_name:
                raise ValueError(f"Failed to translate attribute '{attribute_name}'")
            return ValueTranslator.from_json(value, TravelerView.__attribute_types_by_name[attribute_name])

        return {
            attribute_name: translate_val(attribute_name, value)
            for attribute_name, value in traveler_view.items()
        }


class EventView(DomainConstructedView):
    __attribute_types_by_name = {
        "id": PrefixedUUID,
        "name": str,
        "description": str,
        "span": PositionalRange,
        "tags": Set[Tag],
        "affected_travelers": Set[PrefixedUUID],
        "affected_locations": Set[PrefixedUUID],
        "metadata": Dict[str, str],
    }

    @staticmethod
    def to_json(event: Event) -> dict:
        event_attributes = {attribute_name.replace("_", "", 1): value for attribute_name, value in vars(event).items()}
        return {
            attribute_name: ValueTranslator.to_json(event_attributes[attribute_name])
            for attribute_name in EventView.__attribute_types_by_name.keys()
        }

    @staticmethod
    def kwargs_from_json(event_view: dict) -> dict:
        def translate_val(attribute_name, value):
            if attribute_name not in EventView.__attribute_types_by_name:
                raise ValueError(f"Failed to translate attribute '{attribute_name}' when constructing {Event.__name__}")
            return ValueTranslator.from_json(value, EventView.__attribute_types_by_name[attribute_name])

        return {
            attribute_name: translate_val(attribute_name, value)
            for attribute_name, value in event_view.items()
        }
