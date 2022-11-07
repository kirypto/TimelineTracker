from json import dumps
from re import match
from typing import Dict, Union

from domain.base_entity import BaseEntity


JsonType = Union[str, int, float, bool, dict, list]


class AttributedEntity(BaseEntity):
    _attributes: Dict[str, JsonType]

    @property
    def attributes(self) -> Dict[str, JsonType]:
        return dict(self._attributes)

    def __init__(self, *, attributes: Dict[str, JsonType] = None, **kwargs) -> None:
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
        return hash((AttributedEntity, dumps(self._attributes), super().__hash__()))

    def _validate_attributes(self, attributes: Dict[str, JsonType]) -> Dict[str, JsonType]:
        if not isinstance(attributes, dict):
            raise TypeError(f"{self.__class__.__name__} attribute 'attributes' must be a dictionary")
        stripped_attributes = {}
        for key, value in attributes.items():
            if type(key) is not str:
                raise TypeError(f"{self.__class__.__name__} attribute 'attributes' dictionary keys must be strings, was {type(key)}")
            key = key.strip()
            if not match(r"^[\w\-.]+$", key):
                raise ValueError(f"{self.__class__.__name__} attribute 'attributes' dictionary keys must be non-empty and can only contain "
                                 f"alphanumeric, underscore, dash, and decimal characters; was '{key}'")

            is_value_valid = True
            try:
                dumps(value)
            except (TypeError, ValueError):
                is_value_valid = False
            if not is_value_valid:
                raise TypeError(f"{self.__class__.__name__} attribute 'attributes' dictionary must have values that are json "
                                f"serializable; the following was not: '{value}'")

            stripped_attributes[key] = value
        return stripped_attributes
