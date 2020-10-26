from typing import Generic, TypeVar, Any


T = TypeVar("T")


def _is_comparable_type(var: Any) -> bool:
    class_ = var.__class__
    return ((class_.__eq__ != object.__eq__ or class_.__ne__ != object.__ne__)
            and (class_.__lt__ != object.__lt__ or class_.__gt__ != object.__gt__))


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

    def __init__(self, *, low: T, high: T) -> None:
        if type(low) is not type(high):
            raise TypeError("Arguments 'low' and 'high' must be of the same type")
        if not _is_comparable_type(low):
            raise TypeError("Arguments must be of a comparable type")
        if low > high:
            raise ValueError("Argument 'low' must be less than or equal to 'high'")
        self._low = low
        self._high = high

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Range):
            return False
        return self._low == other._low and self._high == other._high

    def __hash__(self) -> int:
        return hash((self.__class__, self._low, self._high))

    def includes(self, value: T) -> bool:
        if type(value) is not self.type:
            raise TypeError("Argument 'value' must be of same type as range")
        return self._low <= value <= self._high
