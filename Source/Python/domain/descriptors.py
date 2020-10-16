from re import match


class NamedEntity:
    _name: str

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, *, name: str = "", **kwargs) -> None:
        if not isinstance(name, str) or not match(r"^[\w\- ]*$", name):
            raise ValueError("name must be a string with only alphanumeric, underscore, dash, and space characters")
        self._name = name
        super().__init__(**kwargs)


class DescribedEntity:
    _description: str

    @property
    def description(self) -> str:
        return self._description

    def __init__(self, *, description: str = "", **kwargs) -> None:
        if not isinstance(description, str):
            raise ValueError("description must be a string")
        self._description = description
        super().__init__(**kwargs)

