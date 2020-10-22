from typing import Tuple


class LocationsRequestHandler:
    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        print(request_body)
        return {
            "test": "Blarg"
        }, 200
