from json import loads
from pathlib import Path
from typing import Any

from flask_unittest import ClientTestCase

from adapter.persistence.in_memory_repositories import InMemoryEventRepository, InMemoryTravelerRepository, InMemoryLocationRepository, \
    InMemoryWorldRepository
from test_helpers import get_fully_qualified_name
from test_helpers.anons import anon_string, anon_route


_PORT = 54321
_HOST = "localhost"
_APP_CONFIG = {
    "repositories_config": {
        "world_repo_class_path": get_fully_qualified_name(InMemoryWorldRepository),
        "location_repo_class_path": get_fully_qualified_name(InMemoryLocationRepository),
        "traveler_repo_class_path": get_fully_qualified_name(InMemoryTravelerRepository),
        "event_repo_class_path": get_fully_qualified_name(InMemoryEventRepository),
    },
    "resources_folder_path": Path(__file__).parents[4].joinpath("Source/Resources/").resolve().as_posix(),
}
_AUTH_CONFIG = {
    "auth_callback_route": anon_route(),
    "client_id": anon_string(),
}


def construct_flask_app():
    # noinspection PyProtectedMember
    from adapter.runners.flask_app import _create_timeline_tracker_flask_app
    return _create_timeline_tracker_flask_app(_APP_CONFIG, _AUTH_CONFIG, anon_string())


def parse_json(json_bytes: bytes) -> Any:
    return loads(json_bytes.decode("utf-8"))


class StaticallyServedResourceTest(ClientTestCase):
    app = construct_flask_app()

    def test__get_statically_served__should_return_api_spec__when_static_api_spec_route_given(self, client) -> None:
        # Arrange

        # Act
        actual = client.get("/static/APISpec/apiSpecification.json")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual("Timeline Tracker API", parse_json(actual.data)["info"]["title"])
