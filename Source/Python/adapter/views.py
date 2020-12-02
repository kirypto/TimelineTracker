from typing import Any, Set, List
from uuid import UUID

from domain.collections import Range
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.positions import PositionalRange, PositionalMove, Position, MovementType
from domain.tags import Tag
from domain.travelers import Traveler


class _ValueTranslator:
    __pass_through_types = [int, float, bool, str]
    __to_str_types = [PrefixedUUID, Tag]

    @staticmethod
    def to_json(value: Any) -> Any:
        if type(value) in _ValueTranslator.__pass_through_types:
            return value
        if type(value) in _ValueTranslator.__to_str_types:
            return str(value)
        if type(value) in {set, list}:
            return [_ValueTranslator.to_json(inner_val) for inner_val in value]
        if type(value) is Range:
            range_: Range = value
            return {"low": range_.low, "high": range_.high}
        if type(value) is PositionalRange:
            positional_range: PositionalRange = value
            return {
                "latitude": _ValueTranslator.to_json(positional_range.latitude),
                "longitude": _ValueTranslator.to_json(positional_range.longitude),
                "altitude": _ValueTranslator.to_json(positional_range.altitude),
                "continuum": _ValueTranslator.to_json(positional_range.continuum),
                "reality": _ValueTranslator.to_json(positional_range.reality),
            }
        if type(value) is Position:
            position: Position = value
            return {
                "latitude": _ValueTranslator.to_json(position.latitude),
                "longitude": _ValueTranslator.to_json(position.longitude),
                "altitude": _ValueTranslator.to_json(position.altitude),
                "continuum": _ValueTranslator.to_json(position.continuum),
                "reality": _ValueTranslator.to_json(position.reality),
            }
        if type(value) is PositionalMove:
            positional_move: PositionalMove = value
            return {
                "position": _ValueTranslator.to_json(positional_move.position),
                "movement_type": _ValueTranslator.to_json(positional_move.movement_type),
            }
        if type(value) is MovementType:
            movement_type: MovementType = value
            return movement_type.value
        raise TypeError(f"Unsupported type {type(value)}")

    @staticmethod
    def from_json(value: Any, type_: type) -> Any:
        if type_ in _ValueTranslator.__pass_through_types:
            return type_(value)
        if type_ is PrefixedUUID:
            prefixed_uuid_raw: str = value
            prefix, uuid = prefixed_uuid_raw.split("-", 1)
            return PrefixedUUID(prefix, UUID(uuid))
        if type_ is PositionalRange:
            positional_range_json: dict = value
            return PositionalRange(**{
                "latitude": _ValueTranslator.from_json(positional_range_json["latitude"], Range[float]),
                "longitude": _ValueTranslator.from_json(positional_range_json["longitude"], Range[float]),
                "altitude": _ValueTranslator.from_json(positional_range_json["altitude"], Range[float]),
                "continuum": _ValueTranslator.from_json(positional_range_json["continuum"], Range[float]),
                "reality": _ValueTranslator.from_json(positional_range_json["reality"], Range[int]),
            })
        if type_ is Range[float]:
            range_json: dict = value
            return Range(**{
                "low": _ValueTranslator.from_json(range_json["low"], float),
                "high": _ValueTranslator.from_json(range_json["high"], float),
            })
        if type_ is Range[int]:
            range_json: dict = value
            return Range(**{
                "low": _ValueTranslator.from_json(range_json["low"], int),
                "high": _ValueTranslator.from_json(range_json["high"], int),
            })
        if type_ is Set[Tag]:
            tags_json: list = value
            return {_ValueTranslator.from_json(tag, Tag) for tag in tags_json}
        if type_ is Tag:
            tag_raw: str = value
            return Tag(tag_raw)
        if type_ is List[PositionalMove]:
            movements_json: list = value
            return [_ValueTranslator.from_json(move, PositionalMove) for move in movements_json]
        if type_ is PositionalMove:
            positional_movement_json: dict = value
            return PositionalMove(**{
                "position": _ValueTranslator.from_json(positional_movement_json["position"], Position),
                "movement_type": _ValueTranslator.from_json(positional_movement_json["movement_type"], MovementType),
            })
        if type_ is Position:
            position_json: dict = value
            return Position(**{
                "latitude": _ValueTranslator.from_json(position_json["latitude"], float),
                "longitude": _ValueTranslator.from_json(position_json["longitude"], float),
                "altitude": _ValueTranslator.from_json(position_json["altitude"], float),
                "continuum": _ValueTranslator.from_json(position_json["continuum"], float),
                "reality": _ValueTranslator.from_json(position_json["reality"], int),
            })
        if type_ is MovementType:
            movement_type_raw: str = value
            return MovementType(movement_type_raw)
        raise TypeError(f"Unsupported type {type_}")


class PrefixedIdView:
    @staticmethod
    def to_json(location_id: PrefixedUUID) -> str:
        return _ValueTranslator.to_json(location_id)


class LocationIdView(PrefixedIdView):
    @staticmethod
    def from_json(location_id_str: str) -> PrefixedUUID:
        if not location_id_str.startswith("location-"):
            raise ValueError(f"Cannot parse location id from '{location_id_str}")
        return _ValueTranslator.from_json(location_id_str, PrefixedUUID)


class TravelerIdView(PrefixedIdView):
    @staticmethod
    def from_json(traveler_id_str: str) -> PrefixedUUID:
        if not traveler_id_str.startswith("traveler-"):
            raise ValueError(f"Cannot parse traveler id from '{traveler_id_str}")
        return _ValueTranslator.from_json(traveler_id_str, PrefixedUUID)


class LocationView:
    __attribute_types_by_name = {
        "id": PrefixedUUID,
        "name": str,
        "description": str,
        "span": PositionalRange,
        "tags": Set[Tag]
    }

    @staticmethod
    def to_json(location: Location) -> dict:
        location_attributes = {attribute_name.replace("_", "", 1): value for attribute_name, value in vars(location).items()}
        return {
            attribute_name: _ValueTranslator.to_json(location_attributes[attribute_name])
            for attribute_name in LocationView.__attribute_types_by_name.keys()
        }

    @staticmethod
    def kwargs_from_json(location_view: dict) -> dict:
        def translate_val(attribute_name, value):
            if attribute_name not in LocationView.__attribute_types_by_name:
                raise ValueError(f"Failed to translate attribute '{attribute_name}'")
            return _ValueTranslator.from_json(value, LocationView.__attribute_types_by_name[attribute_name])

        return {
            attribute_name: translate_val(attribute_name, value)
            for attribute_name, value in location_view.items()
        }


class TravelerView:
    __attribute_types_by_name = {
        "id": PrefixedUUID,
        "name": str,
        "description": str,
        "journey": List[PositionalMove],
        "tags": Set[Tag]
    }

    @staticmethod
    def to_json(traveler: Traveler) -> dict:
        traveler_attributes = {attribute_name.replace("_", "", 1): value for attribute_name, value in vars(traveler).items()}
        return {
            attribute_name: _ValueTranslator.to_json(traveler_attributes[attribute_name])
            for attribute_name in TravelerView.__attribute_types_by_name.keys()
        }

    @staticmethod
    def kwargs_from_json(traveler_view: dict) -> dict:
        def translate_val(attribute_name, value):
            if attribute_name not in TravelerView.__attribute_types_by_name:
                raise ValueError(f"Failed to translate attribute '{attribute_name}'")
            return _ValueTranslator.from_json(value, TravelerView.__attribute_types_by_name[attribute_name])

        return {
            attribute_name: translate_val(attribute_name, value)
            for attribute_name, value in traveler_view.items()
        }
