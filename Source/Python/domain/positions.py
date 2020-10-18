class Position:
    _latitude: float
    _longitude: float
    _altitude: float
    _continuum: float
    _reality: int

    @property
    def latitude(self) -> float:
        return self._latitude

    @property
    def longitude(self) -> float:
        return self._longitude

    @property
    def altitude(self) -> float:
        return self._altitude

    @property
    def continuum(self) -> float:
        return self._continuum

    @property
    def reality(self) -> int:
        return self._reality

    def __init__(self, *, latitude: float, longitude: float, altitude: float, continuum: float, reality: int, **kwargs) -> None:
        def validate_type(value, acceptable_types):
            if type(value) not in acceptable_types:
                raise ValueError(f"non-numeric value")
            return acceptable_types[0](value)

        self._latitude = validate_type(latitude, [float, int])
        self._longitude = validate_type(longitude, [float, int])
        self._altitude = validate_type(altitude, [float, int])
        self._continuum = validate_type(continuum, [float, int])
        self._reality = validate_type(reality, [int])
        super().__init__(**kwargs)


class PositionalRange:
    pass
