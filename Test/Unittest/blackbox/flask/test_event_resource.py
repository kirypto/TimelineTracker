from copy import copy
from json import loads
from typing import Any

from flask_unittest import ClientTestCase

from Test.Unittest.test_helpers.anons import anon_event, anon_location, anon_traveler
from adapter.views import JsonTranslator
from domain.positions import PositionalMove, Position, MovementType


_PORT = 54321
_HOST = "localhost"
_APP_CONFIG = {
    "repositories_config": {
        "repository_type": "memory",
    },
}


def construct_flask_app():
    # noinspection PyProtectedMember
    from adapter.runners.flask.flask_app import _create_timeline_tracker_flask_app
    return _create_timeline_tracker_flask_app(_APP_CONFIG)


def parse_json(json_bytes: bytes) -> Any:
    return loads(json_bytes.decode("utf-8"))


class EventResourceTest(ClientTestCase):
    app = construct_flask_app()

    def test__post_event__should_create_event__when_all_args_provided(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())

        # Act
        actual = client.post("/api/event", json=body)

        # Assert
        self.assertEqual(201, actual.status_code)
        self.assertIn("id", parse_json(actual.data))

    def test__post_event__should_create_event__optional_args_left_out(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        optional_arg_names = {"description", "metadata", "tags"}
        for arg_name in optional_arg_names:
            body = copy(body)
            body.pop(arg_name)

            # Act
            actual = client.post("/api/event", json=body)

            # Assert
            self.assertEqual(201, actual.status_code, msg=f"POST failed when '{arg_name}' was not provided")

    def test__get_events__should_return_existing_events(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post("/api/event", json=body)
        expected_id = parse_json(response.data)["id"]

        # Act
        actual = client.get(f"/api/events")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertIn(expected_id, parse_json(actual.data))

    def test__get_event__should_return_existing_event(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]

        # Act

        actual = client.get(f"/api/event/{event_id}")

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__delete_event__should_remove(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post("/api/event", json=body)
        event_id = parse_json(response.data)["id"]

        # Act
        actual = client.delete(f"/api/event/{event_id}")

        # Assert
        self.assertEqual(204, actual.status_code)
        self.assertEqual(404, client.get(f"/api/event/{event_id}").status_code)

    def test__patch_event__should_allow_editing_name(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event(tags=set(), metadata={}))
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["name"] = "New Name"
        patch = [{"op": "replace", "path": "/name", "value": "New Name"}]

        # Act
        actual = client.patch(f"/api/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_tags(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["tags"][0] = "new-tag"
        patch = [{"op": "replace", "path": "/tags/0", "value": "new-tag"}]

        # Act
        actual = client.patch(f"/api/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_span(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["span"]["continuum"]["low"] = -4321.01234
        patch = [{"op": "replace", "path": "/span/continuum/low", "value": -4321.01234}]

        # Act
        actual = client.patch(f"/api/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_metadata(self, client) -> None:
        # Arrange
        body = JsonTranslator.to_json(anon_event())
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["metadata"]["new-key"] = "new-val"
        patch = [{"op": "add", "path": "/metadata/new-key", "value": "new-val"}]

        # Act
        actual = client.patch(f"/api/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_affected_locations(self, client) -> None:
        # Arrange
        event = anon_event()
        body = JsonTranslator.to_json(event)
        location = anon_location(span=event.span)
        location_id = parse_json(client.post("/api/location", json=JsonTranslator.to_json(location)).data)["id"]
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["affected_locations"].append(location_id)
        patch = [{"op": "add", "path": "/affected_locations/0", "value": location_id}]

        # Act
        actual = client.patch(f"/api/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))

    def test__patch_event__should_allow_editing_affected_travelers(self, client) -> None:
        # Arrange
        event = anon_event()
        body = JsonTranslator.to_json(event)
        traveler = anon_traveler(journey=[PositionalMove(movement_type=MovementType.IMMEDIATE, position=Position(
            latitude=event.span.latitude.low,
            altitude=event.span.altitude.low,
            longitude=event.span.longitude.low,
            continuum=event.span.continuum.low,
            reality=event.span.reality.low,
        ))])
        traveler_id = parse_json(client.post("/api/traveler", json=JsonTranslator.to_json(traveler)).data)["id"]
        response = client.post("/api/event", json=body)
        expected_json = parse_json(response.data)
        event_id = expected_json["id"]
        expected_json["affected_travelers"].append(traveler_id)
        patch = [{"op": "add", "path": "/affected_travelers/0", "value": traveler_id}]

        # Act
        actual = client.patch(f"/api/event/{event_id}", json=patch)

        # Assert
        self.assertEqual(200, actual.status_code)
        self.assertEqual(expected_json, parse_json(actual.data))
