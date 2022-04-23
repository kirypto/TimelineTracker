from copy import copy
from json import loads
from pathlib import Path
from typing import Any

from flask.testing import FlaskClient
from flask_unittest import ClientTestCase

from adapter.persistence.in_memory_repositories import InMemoryWorldRepository, InMemoryLocationRepository, InMemoryTravelerRepository, \
    InMemoryEventRepository
from application.requests.data_forms import JsonTranslator
from domain.ids import PrefixedUUID
from domain.positions import PositionalMove, Position, MovementType
from test_helpers import get_fully_qualified_name
from test_helpers.anons import anon_event, anon_location, anon_traveler, anon_float, anon_string, anon_route, anon_name, anon_prefixed_id


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


class EventResourceTest(ClientTestCase):
    app = construct_flask_app()
    world_id: PrefixedUUID

    def setUp(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            session["profile"] = {"user_id": anon_string(), "name": anon_name()}

        self.world_id = anon_prefixed_id(prefix="world")

    def tearDown(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            del session["profile"]

    def test__post_event__should_create_event__when_all_args_provided(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())

        # Act
        actual = client.post(f"/api/world/{self.world_id}/event", json=body)

        # Assert
        self.assertEqual(201, actual.status_code)
        self.assertIn("id", parse_json(actual.data))

    def test__post_event__should_create_event__optional_args_left_out(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        optional_arg_names = {"description", "attributes", "tags"}
        for arg_name in optional_arg_names:
            body = copy(body)
            body.pop(arg_name)

            # Act
            actual = client.post(f"/api/world/{self.world_id}/event", json=body)

            # Assert
            self.assertEqual(201, actual.status_code, msg=f"POST failed when '{arg_name}' was not provided")

    def test__get_events__should_return_existing_events(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_id = parse_json(response.data)["id"]

        # Act
        actual = client.get(f"/api/world/{self.world_id}/events")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertIn(expected_id, parse_json(actual.data))

    def test__get_event__should_return_existing_event(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]

        # Act

        actual = client.get(f"/api/world/{self.world_id}/event/{event_id}")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__delete_event__should_remove(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        event_id = parse_json(response.data)["id"]

        # Act
        actual = client.delete(f"/api/world/{self.world_id}/event/{event_id}")

        # Assert
        self.assertEqual(204, actual.status_code)
        self.assertEqual(404, client.get(f"/api/world/{self.world_id}/event/{event_id}").status_code)

    def test__patch_event__should_allow_editing_name(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event(tags=set(), attributes={}))
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["name"] = "New Name"
        patch = [{"op": "replace", "path": "/name", "value": "New Name"}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_tags(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["tags"][0] = "new-tag"
        patch = [{"op": "replace", "path": "/tags/0", "value": "new-tag"}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_span(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_continuum_low = anon_float(-999999.9, expected_json["span"]["continuum"]["high"])
        expected_json["span"]["continuum"]["low"] = expected_continuum_low
        patch = [{"op": "replace", "path": "/span/continuum/low", "value": expected_continuum_low}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_attributes(self, client: FlaskClient) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["attributes"]["new-key"] = "new-val"
        patch = [{"op": "add", "path": "/attributes/new-key", "value": "new-val"}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_affected_locations(self, client: FlaskClient) -> None:
        # Arrange
        event = anon_event()
        body = JsonTranslator.to_json(event)
        location = anon_location(span=event.span)
        location_id = parse_json(client.post(f"/api/world/{self.world_id}/location", json=JsonTranslator.to_json(location)).data)["id"]
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["affected_locations"].append(location_id)
        patch = [{"op": "add", "path": "/affected_locations/0", "value": location_id}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_affected_travelers(self, client: FlaskClient) -> None:
        # Arrange
        event = anon_event()
        body = JsonTranslator.to_json(event)
        traveler = anon_traveler(journey=[PositionalMove(movement_type=MovementType.IMMEDIATE, position=Position(
            latitude=event.span.latitude.low,
            altitude=event.span.altitude.low,
            longitude=event.span.longitude.low,
            continuum=event.span.continuum.low,
            reality=next(iter(event.span.reality)),
        ))])
        traveler_id = parse_json(client.post(f"/api/world/{self.world_id}/traveler", json=JsonTranslator.to_json(traveler)).data)["id"]
        response = client.post(f"/api/world/{self.world_id}/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["affected_travelers"].append(traveler_id)
        patch = [{"op": "add", "path": "/affected_travelers/0", "value": traveler_id}]

        # Act
        actual = client.patch(f"/api/world/{self.world_id}/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))
