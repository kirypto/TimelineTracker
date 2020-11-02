from __future__ import annotations

from typing import Any, List

from domain.base_entity import BaseEntity
from domain.collections import Range


class Position:
    _latitude: float
    _longitude: float
    _altitude: float
    _continuum: float
    _reality: int

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
    def reality(self) -> int:
        return self._reality

    def __init__(self, *, latitude: float, longitude: float, altitude: float, continuum: float, reality: int, **kwargs) -> None:
        def validate_type(value, acceptable_types):
            if type(value) not in acceptable_types:
                raise TypeError(f"Invalid value '{value}', must be one of {acceptable_types}")
            return acceptable_types[0](value)

        self._latitude = validate_type(latitude, [float, int])
        self._longitude = validate_type(longitude, [float, int])
        self._altitude = validate_type(altitude, [float, int])
        self._continuum = validate_type(continuum, [float, int])
        self._reality = validate_type(reality, [int])
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


class PositionalRange:
    _latitude: Range[float]
    _longitude: Range[float]
    _altitude: Range[float]
    _continuum: Range[float]
    _reality: Range[int]

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
    def reality(self) -> Range[int]:
        return self._reality

    def __init__(self, *, latitude: Range[float], longitude: Range[float], altitude: Range[float], continuum: Range[float], reality: Range[int],
                 **kwargs):
        def _validate_range(argument_name: str, range_: Range, acceptable_types: List[type]):
            if not isinstance(range_, Range):
                raise TypeError(f"Argument '{argument_name}' must be a {Range}")
            if range_.type not in acceptable_types:
                raise TypeError(f"Argument '{argument_name}' must be a Range of one of {acceptable_types}")
            return Range(low=acceptable_types[0](range_.low), high=acceptable_types[0](range_.high))

        self._latitude = _validate_range("latitude", latitude, [float, int])
        self._longitude = _validate_range("longitude", longitude, [float, int])
        self._altitude = _validate_range("altitude", altitude, [float, int])
        self._continuum = _validate_range("continuum", continuum, [float, int])
        self._reality = _validate_range("reality", reality, [int])
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


class SpanningEntity(BaseEntity):
    _span: PositionalRange

    @property
    def span(self) -> PositionalRange:
        return self._span

    def __init__(self, *, span, **kwargs):
        if not isinstance(span, PositionalRange):
            raise TypeError(f"Argument 'span' must be a {PositionalRange}")
        self._span = span
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SpanningEntity):
            return False
        return self._span == other._span and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((self.__class__, self._span, super().__hash__()))
