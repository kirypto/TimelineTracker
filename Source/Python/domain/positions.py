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
                raise ValueError(f"Invalid value '{value}', must be one of {acceptable_types}")
            return acceptable_types[0](value)

        self._latitude = validate_type(latitude, [float, int])
        self._longitude = validate_type(longitude, [float, int])
        self._altitude = validate_type(altitude, [float, int])
        self._continuum = validate_type(continuum, [float, int])
        self._reality = validate_type(reality, [int])
        super().__init__(**kwargs)


class PositionalRange:
    _latitude_low: float
    _latitude_high: float
    _longitude_low: float
    _longitude_high: float
    _altitude_low: float
    _altitude_high: float
    _continuum_low: float
    _continuum_high: float
    _reality_low: int
    _reality_high: int

    @property
    def latitude_low(self) -> float:
        return self._latitude_low

    @property
    def latitude_high(self) -> float:
        return self._latitude_high

    @property
    def longitude_low(self) -> float:
        return self._longitude_low

    @property
    def longitude_high(self) -> float:
        return self._longitude_high

    @property
    def altitude_low(self) -> float:
        return self._altitude_low

    @property
    def altitude_high(self) -> float:
        return self._altitude_high

    @property
    def continuum_low(self) -> float:
        return self._continuum_low

    @property
    def continuum_high(self) -> float:
        return self._continuum_high

    @property
    def reality_low(self) -> int:
        return self._reality_low

    @property
    def reality_high(self) -> int:
        return self._reality_high

    def __init__(self, *,
                 latitude: float = None, latitude_low: float = None, latitude_high: float = None,
                 longitude: float = None, longitude_low: float = None, longitude_high: float = None,
                 altitude: float = None, altitude_low: float = None, altitude_high: float = None,
                 continuum: float = None, continuum_low: float = None, continuum_high: float = None,
                 reality: float = None, reality_low: float = None, reality_high: float = None,
                 **kwargs):
        def validate_low_and_high(singular, range_low, range_high, acceptable_types):
            singular_given, low_given, high_given = [x is not None for x in (singular, range_low, range_high)]
            if low_given ^ high_given:
                raise ValueError("Must either provide both low/high values or neither for each dimension")
            if singular_given and (low_given or high_given):
                raise ValueError("Cannot provide singular and low/high values simultaneously for the same dimension")
            if not any([singular_given, low_given, high_given]):
                raise ValueError("Must either provide singular value or low/high values for each dimension")
            actual_low, actual_high = (singular, singular) if singular_given else (range_low, range_high)
            if type(actual_low) not in acceptable_types:
                raise ValueError(f"Invalid value '{actual_low}', must be one of {acceptable_types}")
            if type(actual_high) not in acceptable_types:
                raise ValueError(f"Invalid value '{actual_high}', must be one of {acceptable_types}")
            return acceptable_types[0](actual_low), acceptable_types[0](actual_high)

        self._latitude_low, self._latitude_high = validate_low_and_high(latitude, latitude_low, latitude_high, [float, int])
        self._longitude_low, self._longitude_high = validate_low_and_high(longitude, longitude_low, longitude_high, [float, int])
        self._altitude_low, self._altitude_high = validate_low_and_high(altitude, altitude_low, altitude_high, [float, int])
        self._continuum_low, self._continuum_high = validate_low_and_high(continuum, continuum_low, continuum_high, [float, int])
        self._reality_low, self._reality_high = validate_low_and_high(reality, reality_low, reality_high, [int])
        super().__init__(**kwargs)
