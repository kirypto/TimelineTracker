from re import match

from domain.base_entity import BaseEntity


class NamedEntity(BaseEntity):
    _name: str

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, *, name: str, **kwargs) -> None:
        if name is None:
            raise ValueError(f"{self.__class__.__name__} attribute 'name' cannot be {None}")
        if not isinstance(name, str):
            raise TypeError(f"{self.__class__.__name__} attribute 'name' must be of type {str}")
        name = name.strip()
        if len(name) == 0:
            raise ValueError(f"{self.__class__.__name__} attribute 'name' cannot be empty")
        if not match(r"^[\w\-. ]*$", name):
            raise ValueError(f"{self.__class__.__name__} attribute 'name' must contain only alphanumeric, underscore, dash, and space "
                             f"characters")
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
        if description is None:
            raise ValueError(f"{self.__class__.__name__} attribute 'description' cannot be {None}")
        if not isinstance(description, str):
            raise ValueError(f"{self.__class__.__name__} attribute 'description' must be a string")
        self._description = description
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DescribedEntity):
            return False
        return self._description == other._description and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((DescribedEntity, self._description, super().__hash__()))
