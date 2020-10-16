from re import match


class NamedEntity:
    _name: str

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, *, name: str = "", **kwargs):
        if not isinstance(name, str) or not match(r"^[\w\- ]*$", name):
            raise ValueError("name must be a string with only alphanumeric, underscore, dash, and space characters")
        self._name = name
        super().__init__(**kwargs)


class DescribedEntity:
    pass
