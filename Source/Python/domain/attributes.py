from re import match
from typing import Dict

from domain.base_entity import BaseEntity


class AttributedEntity(BaseEntity):
    _attributes: Dict[str, str]

    @property
    def attributes(self) -> Dict[str, str]:
        return dict(self._attributes)

    def __init__(self, *, attributes: Dict[str, str] = None, **kwargs) -> None:
        if attributes is not None:
            attributes = self._validate_attributes(attributes)
        else:
            attributes = {}
        self._attributes = attributes
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AttributedEntity):
            return False
        return self._attributes == other._attributes and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((AttributedEntity, frozenset(self._attributes.items()), super().__hash__()))

    def _validate_attributes(self, attributes: Dict[str, str]) -> Dict[str, str]:
        if not isinstance(attributes, dict):
            raise TypeError(f"{self.__class__.__name__} attribute 'attributes' must be a dictionary")
        stripped_attributes = {}
        for key, value in attributes.items():
            if type(key) is not str:
                raise TypeError(f"{self.__class__.__name__} attribute 'attributes' dictionary keys must be strings, was {type(key)}")
            if type(value) is not str:
                raise TypeError(f"{self.__class__.__name__} attribute 'attributes' dictionary values must be strings, was {type(value)}")
            key = key.strip()
            if not match(r"^[\w\-.]+$", key):
                raise ValueError(f"{self.__class__.__name__} attribute 'attributes' dictionary keys must be non-empty and can only contain "
                                 f"alphanumeric, underscore, dash, and decimal characters; was '{key}'")
            value = value.strip()
            if len(value) == 0:
                raise ValueError(f"{self.__class__.__name__} attribute 'attributes' dictionary values must be non-empty")
            stripped_attributes[key] = value
        return stripped_attributes
