
class BaseEntity:
    def __init__(self, **kwargs) -> None:
        if kwargs:
            raise AttributeError(f"Failed to construct {self.__class__.__name__}, no attributes correspond to the provided arguments: {kwargs}")

    def __eq__(self, other: object) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self.__class__)
