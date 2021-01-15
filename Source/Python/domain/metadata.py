from re import match
from typing import Dict

from domain.base_entity import BaseEntity


class MetadataEntity(BaseEntity):
    _metadata: Dict[str, str]

    @property
    def metadata(self) -> Dict[str, str]:
        return dict(self._metadata)

    def __init__(self, *, metadata: Dict[str, str] = None, **kwargs) -> None:
        if metadata is not None:
            self._validate_metadata(metadata)
        else:
            metadata = {}
        self._metadata = metadata
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetadataEntity):
            return False
        return self._metadata == other._metadata and super().__eq__(other)

    def __hash__(self) -> int:
        return hash((MetadataEntity, frozenset(self._metadata.items()), super().__hash__()))

    def _validate_metadata(self, metadata: Dict[str, str]) -> None:
        if not isinstance(metadata, dict):
            raise TypeError(f"{self.__class__.__name__} attribute 'metadata' must be a dictionary")
        for key, value in metadata.items():
            if type(key) is not str:
                raise TypeError(f"{self.__class__.__name__} attribute 'metadata' dictionary keys must be strings, was {type(key)}")
            elif type(value) is not str:
                raise TypeError(f"{self.__class__.__name__} attribute 'metadata' dictionary values must be strings, was {type(value)}")
            elif not match(r"^[\w\-.]*$", key):
                raise ValueError(f"{self.__class__.__name__} attribute 'metadata' dictionary keys must contain only alphanumeric, underscore, dash, "
                                 f"and space characters; was {value}")
