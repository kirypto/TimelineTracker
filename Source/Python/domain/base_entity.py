
class BaseEntity:
    def __init__(self, **kwargs) -> None:
        if kwargs:
            raise ValueError(f"Unused args provided: {kwargs}")

    def __eq__(self, other: object) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self.__class__)
