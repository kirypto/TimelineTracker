from copy import copy
from json import loads
from pathlib import Path
from typing import Any

from flask.testing import FlaskClient
from flask_unittest import ClientTestCase

from adapter.persistence.in_memory_repositories import InMemoryEventRepository, InMemoryTravelerRepository, InMemoryLocationRepository, \
    InMemoryWorldRepository
from application.requests.data_forms import JsonTranslator
from domain.ids import PrefixedUUID
from test_helpers import get_fully_qualified_name
from test_helpers.anons import anon_traveler, anon_string, anon_route, anon_name, anon_world


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


class TravelerResourceTest(ClientTestCase):
    app = construct_flask_app()
    world_id: PrefixedUUID

    def setUp(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            session["profile"] = {"user_id": anon_string(), "name": anon_name()}
        world_post_body = JsonTranslator.to_json(anon_world())
        world_post_response = client.post(f"/api/world", json=world_post_body)
        self.world_id = JsonTranslator.from_json(world_post_response.json["id"], PrefixedUUID)

    def tearDown(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            del session["profile"]

    def test__post_traveler__should_create_traveler__when_all_args_provided(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())

        # Act
        actual = client.post(f"/api/world/{self.world_id}/traveler", json=body)

        # Assert
        self.assertEqual(201, actual.status_code)
        self.assertIn("id", parse_json(actual.data))

    def test__post_traveler__should_create_traveler__optional_args_left_out(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        optional_arg_names = {"description", "attributes", "tags"}
        for arg_name in optional_arg_names:
            body = copy(body)
            body.pop(arg_name)

            # Act
            actual = client.post(f"/api/world/{self.world_id}/traveler", json=body)

            # Assert
            self.assertEqual(201, actual.status_code, msg=f"POST failed when '{arg_name}' was not provided")

    def test__get_travelers__should_return_existing_travelers(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        expected_id = parse_json(response.data)["id"]

        # Act
        actual = client.get(f"/api/world/{self.world_id}/travelers")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertIn(expected_id, parse_json(actual.data))

    def test__get_traveler__should_return_existing_traveler(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        expected_json = parse_json(response.data)
        traveler_id = expected_json["id"]

        # Act

        actual = client.get(f"/api/world/{self.world_id}/traveler/{traveler_id}")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__delete_traveler__should_remove(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        traveler_id = parse_json(response.data)["id"]

        # Act
        actual = client.delete(f"/api/world/{self.world_id}/traveler/{traveler_id}")

        # Assert
        self.assertEqual(204, actual.status_code)
        self.assertEqual(404, client.get(f"/api/world/{self.world_id}/traveler/{traveler_id}").status_code)

    def test__patch_traveler__should_allow_editing_name(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler(tags=set(), attributes={}))
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        expected_json = parse_json(response.data)
        traveler_id = expected_json["id"]
        expected_json["name"] = "New Name"
        patch = [{"op": "replace", "path": "/name", "value": "New Name"}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/traveler/{traveler_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_traveler__should_allow_editing_tags(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        expected_json = parse_json(response.data)
        traveler_id = expected_json["id"]
        expected_json["tags"][0] = "new-tag"
        patch = [{"op": "replace", "path": "/tags/0", "value": "new-tag"}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/traveler/{traveler_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_traveler__should_allow_editing_journey(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        expected_json = parse_json(response.data)
        traveler_id = expected_json["id"]
        expected_json["journey"][0]["position"]["continuum"] = -4321.01234
        patch = [{"op": "replace", "path": "/journey/0/position/continuum", "value": -4321.01234}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/traveler/{traveler_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_traveler__should_allow_editing_attributes(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_traveler())
        response = client.post(f"/api/world/{self.world_id}/traveler", json=body)
        expected_json = parse_json(response.data)
        traveler_id = expected_json["id"]
        expected_json["attributes"]["new-key"] = "new-val"
        patch = [{"op": "add", "path": "/attributes/new-key", "value": "new-val"}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/traveler/{traveler_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))
