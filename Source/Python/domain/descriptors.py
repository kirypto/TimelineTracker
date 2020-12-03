from re import match

from domain.base_entity import BaseEntity


class NamedEntity(BaseEntity):
    _name: str

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, *, name: str = "", **kwargs) -> None:
        if not isinstance(name, str):
            raise TypeError(f"Argument 'name' must be of type {str}")
        if not match(r"^[\w\-. ]*$", name):
            raise ValueError("Argument 'name' must be contain only alphanumeric, underscore, dash, and space characters")
        self._name = name
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NamedEntity):
            return False
        return self._name == other._name and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((NamedEntity, self._name, super().__hash__()))


class DescribedEntity(BaseEntity):
    _description: str

    @property
    def description(self) -> str:
        return self._description

    def __init__(self, *, description: str = "", **kwargs) -> None:
        if not isinstance(description, str):
            raise ValueError("description must be a string")
        self._description = description
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DescribedEntity):
            return False
        return self._description == other._description and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((DescribedEntity, self._description, super().__hash__()))