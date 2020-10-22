from domain.locations import Location


class LocationView:
    @staticmethod
    def to_json_dict(location: Location) -> dict:
        return {k.removeprefix("_"): str(v) for k, v in vars(location).items()}