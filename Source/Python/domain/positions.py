from __future__ import annotations

from enum import Enum
from math import isinf, isnan
from typing import Any, List

from domain.base_entity import BaseEntity
from domain.collections import Range


class Position:
    _latitude: float
    _longitude: float
    _altitude: float
    _continuum: float
    _reality: float

    @property
    def latitude(self) -> float:
        return self._latitude

    @property
    def longitude(self) -> float:
        return self._longitude

    @property
    def altitude(self) -> float:
        return self._altitude

    @property
    def continuum(self) -> float:
        return self._continuum

    @property
    def reality(self) -> float:
        return self._reality

    def __init__(self, *, latitude: float, longitude: float, altitude: float, continuum: float, reality: float, **kwargs) -> None:
        def validate_type(argument_name, value, acceptable_types):
            if type(value) not in acceptable_types:
                raise TypeError(f"{self.__class__.__name__} attribute '{argument_name}' must be one of types {acceptable_types}, was {type(value)}")
            if isinf(value) or isnan(value):
                raise ValueError(f"{self.__class__.__name__} attribute '{argument_name}' cannot be +/-Infinity or NaN, was {value}")
            return acceptable_types[0](value)

        self._latitude = validate_type("latitude", latitude, [float, int])
        self._longitude = validate_type("longitude", longitude, [float, int])
        self._altitude = validate_type("altitude", altitude, [float, int])
        self._continuum = validate_type("continuum", continuum, [float, int])
        self._reality = validate_type("reality", reality, [float, int])
        if not self._reality.is_integer():
            raise ValueError(f"{self.__class__.__name__} attribute 'reality' must be a whole number, was '{reality}'")
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self._latitude == other._latitude
                and self._longitude == other._longitude
                and self._altitude == other._altitude
                and self._continuum == other._continuum
                and self._reality == other._reality)

    def __hash__(self) -> int:
        return hash((self.__class__, self._latitude, self._longitude, self._altitude, self._continuum, self._reality))

    def __str__(self) -> str:
        return f"({self._latitude},{self._longitude},{self._altitude},{self._continuum},{self._reality})"


class PositionalRange:
    _latitude: Range[float]
    _longitude: Range[float]
    _altitude: Range[float]
    _continuum: Range[float]
    _reality: Range[float]

    @property
    def latitude(self) -> Range[float]:
        return self._latitude

    @property
    def longitude(self) -> Range[float]:
        return self._longitude

    @property
    def altitude(self) -> Range[float]:
        return self._altitude

    @property
    def continuum(self) -> Range[float]:
        return self._continuum

    @property
    def reality(self) -> Range[float]:
        return self._reality

    def __init__(self, *, latitude: Range[float], longitude: Range[float], altitude: Range[float], continuum: Range[float], reality: Range[float],
                 **kwargs):
        def _validate_range(argument_name: str, range_: Range, acceptable_types: List[type]):
            if not isinstance(range_, Range):
                raise TypeError(f"{self.__class__.__name__} attribute '{argument_name}' must be a {Range.__name__}")
            if range_.type not in acceptable_types:
                raise TypeError(f"{self.__class__.__name__} attribute '{argument_name}' must be a {Range.__name__} of one of {acceptable_types}")
            if isnan(range_.low) or isnan(range_.high):
                raise ValueError(f"{self.__class__.__name__} attribute '{argument_name}' contained NaN")
            return Range(low=acceptable_types[0](range_.low), high=acceptable_types[0](range_.high))

        self._latitude = _validate_range("latitude", latitude, [float, int])
        self._longitude = _validate_range("longitude", longitude, [float, int])
        self._altitude = _validate_range("altitude", altitude, [float, int])
        self._continuum = _validate_range("continuum", continuum, [float, int])
        self._reality = _validate_range("reality", reality, [float, int])
        if (not (self._reality.low.is_integer() or isinf(self._reality.low)) or
                not (self._reality.high.is_integer() or isinf(self._reality.high))):
            raise ValueError(f"{self.__class__.__name__} attribute 'reality' must be a range Range of two whole numbers, was {self._reality}")

        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PositionalRange):
            return NotImplemented
        return (self._latitude == other._latitude
                and self._longitude == other._longitude
                and self._altitude == other._altitude
                and self._continuum == other._continuum
                and self._reality == other._reality)

    def __hash__(self) -> int:
        return hash((self.__class__, self._latitude, self._longitude, self._altitude, self._continuum, self._reality))

    def __str__(self) -> str:
        return f"({self._latitude},{self._longitude},{self._altitude},{self._continuum},{self._reality})"

    def includes(self, position: Position) -> bool:
        if not isinstance(position, Position):
            raise TypeError(f"Argument must be of type {Position.__name__}")
        return (self._latitude.includes(position.latitude)
                and self._longitude.includes(position.longitude)
                and self._altitude.includes(position.altitude)
                and self._continuum.includes(position.continuum)
                and self._reality.includes(position.reality))

    def intersects(self, positional_range: PositionalRange) -> bool:
        if not isinstance(positional_range, PositionalRange):
            raise TypeError(f"Argument must be of type {PositionalRange.__name__}")
        return (self._latitude.intersects(positional_range.latitude)
                and self._longitude.intersects(positional_range.longitude)
                and self._altitude.intersects(positional_range.altitude)
                and self._continuum.intersects(positional_range.continuum)
                and self._reality.intersects(positional_range.reality))

    @staticmethod
    def _range_includes(low: Any, high: Any, value: Any) -> bool:
        return low <= value <= high

    @staticmethod
    def _range_intersects(a_low: Any, a_high: Any, b_low: Any, b_high: Any) -> bool:
        return ((a_low <= b_low <= a_high)
                or (a_low <= b_high <= a_high)
                or (a_low <= b_low and a_high >= b_high)
                or (b_low <= a_low and b_high >= a_high))


class MovementType(Enum):
    IMMEDIATE = 'immediate'
    INTERPOLATED = 'interpolated'


class PositionalMove:
    _position: Position
    _movement_type: MovementType

    @property
    def position(self) -> Position:
        return self._position

    @property
    def movement_type(self) -> MovementType:
        return self._movement_type

    def __init__(self, *, position: Position, movement_type: MovementType) -> None:
        if not isinstance(position, Position):
            raise TypeError(f"{self.__class__.__name__} attribute 'position' must be of type {Position}")
        if not isinstance(movement_type, MovementType):
            raise TypeError(f"{self.__class__.__name__} attribute 'movement_type' must be of type {MovementType}")
        self._position = position
        self._movement_type = movement_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PositionalMove):
            return False
        return (self._position == other._position
                and self._movement_type == other._movement_type)

    def __hash__(self) -> int:
        return hash((self.__class__, self._position, self._movement_type))


class SpanningEntity(BaseEntity):
    _span: PositionalRange

    @property
    def span(self) -> PositionalRange:
        return self._span

    def __init__(self, *, span, **kwargs) -> None:
        if not isinstance(span, PositionalRange):
            raise TypeError(f"{self.__class__.__name__} attribute 'span' must be a {PositionalRange.__name__}")
        self._span = span
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpanningEntity):
            return False
        return self._span == other._span and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((SpanningEntity, self._span, super().__hash__()))


class JourneyingEntity(BaseEntity):
    _journey: List[PositionalMove]

    @property
    def journey(self) -> List[PositionalMove]:
        return list(self._journey)

    def __init__(self, journey: List[PositionalMove], **kwargs) -> None:
        if not isinstance(journey, list) or any([not isinstance(move, PositionalMove) for move in journey]):
            raise TypeError(f"{self.__class__.__name__} attribute 'journey' must be a list of {PositionalMove.__name__}s")
        self.validate_journey(journey)
        self._journey = journey
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JourneyingEntity):
            return False
        return self._journey == other._journey and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((JourneyingEntity, tuple(self._journey), super().__hash__()))

    @staticmethod
    def validate_journey(journey: List[PositionalMove]) -> None:
        if not journey:
            raise ValueError(f"Argument 'journey' must not be empty")
        if journey[0].movement_type != MovementType.IMMEDIATE:
            raise ValueError(f"Invalid Journey: Initial position in journey must be movement_type={MovementType.IMMEDIATE}")
        last_position = None
        for positional_move in journey:
            if last_position is None:
                last_position = positional_move.position
                continue
            if positional_move.movement_type == MovementType.INTERPOLATED:
                if positional_move.position.reality != last_position.reality:
                    raise ValueError(f"Invalid journey: Cannot interpolate across realities. (problematic move was: {positional_move}, which "
                                     f"succeeded {last_position})")
                elif positional_move.position.continuum <= last_position.continuum:
                    raise ValueError(f"Invalid journey: Cannot interpolate backwards in continuum. (problematic move was: {positional_move}, which "
                                     f"succeeded {last_position})")
            last_position = positional_move.position
