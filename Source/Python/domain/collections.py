from __future__ import annotations

from functools import total_ordering
from typing import Generic, TypeVar, Any


T = TypeVar("T")


def _is_comparable_type(var: Any) -> bool:
    class_ = var.__class__
    return ((class_.__eq__ != object.__eq__ or class_.__ne__ != object.__ne__)
            and (class_.__lt__ != object.__lt__ or class_.__gt__ != object.__gt__))


@total_ordering
class Range(Generic[T]):
    _low: T
    _high: T

    @property
    def low(self) -> T:
        return self._low

    @property
    def high(self) -> T:
        return self._high

    @property
    def type(self) -> type:
        return type(self._low)

    def __init__(self, low: T, high: T) -> None:
        if type(low) is not type(high):
            raise TypeError(f"{self.__class__.__name__} attributes 'low' and 'high' must be of the same type")
        if not _is_comparable_type(low):
            raise TypeError(f"{self.__class__.__name__} attributes 'low' and 'high' must be of a comparable types")
        self._low = min(low, high)
        self._high = max(low, high)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Range) or self.type != other.type:
            raise ValueError(f"Cannot compare with {other}")
        return self._low == other._low and self._high == other._high

    def __lt__(self, other: Range[T]) -> bool:
        if not isinstance(other, Range) or self.type != other.type:
            raise ValueError(f"Cannot compare with {other}")
        if self._low != other._low:
            return self._low < other._low
        else:
            return self._high < other._high

    def __hash__(self) -> int:
        return hash((self.__class__, self._low, self._high))

    def __str__(self) -> str:
        return f"[{self._low},{self._high}]"

    def __repr__(self) -> str:
        return f"{Range.__name__}({repr(self._low)},{repr(self._high)})"

    def includes(self, value: T) -> bool:
        if type(value) is not self.type:
            raise TypeError("Argument 'value' must be of same type as range")
        return self._low <= value <= self._high

    def intersects(self, other: Range[T]) -> bool:
        if not isinstance(other, Range):
            raise TypeError(f"Argument 'other' must be a {self.__class__}")
        if other.type is not self.type:
            raise TypeError(f"Argument 'other' must be of same type as queried range")
        return ((self._low <= other._low <= self._high)
                or (self._low <= other._high <= self._high)
                or (self._low <= other._low and self._high >= other._high)
                or (other._low <= self._low and other._high >= self._high))
