from json import loads, dumps
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import UUID

from Test.Unittest.test_helpers.controllers import TestableRESTController
from application.main import TimelineTrackerApp
from application.requests.rest import RESTMethod
from domain.ids import PrefixedUUID
from test_helpers.anons import anon_profile
from test_helpers.specifications import APISpecification


_CONFIG = {
    "resources_folder_path": Path(__file__).parents[4].joinpath("Source/Resources"),
    "repositories_config": {
        "repository_type": "memory"
    },
}


def dummy_id_generator(prefix: str) -> PrefixedUUID:
    return PrefixedUUID(prefix, UUID("abad1dea-0000-4000-8000-000000000000"))


class TestAPISpecification(TestCase):
    controller: TestableRESTController
    api_spec: APISpecification

    @patch("application.main.RESTControllersFactory")
    def setUp(
            self, rest_controller_factory_class_mock: MagicMock,
    ) -> None:
        self.controller = TestableRESTController()
        timeline_tracker_application = TimelineTrackerApp(**_CONFIG)

        def rest_controller_factory(**_):
            factory_result = MagicMock()  # Container to store rest_controller property
            factory_result.rest_controller = self.controller
            return factory_result

        rest_controller_factory_class_mock.side_effect = rest_controller_factory

        timeline_tracker_application.initialize_controllers(rest_controller_config={})

        api_spec_file = Path(__file__).parents[4].joinpath("Source/Resources/StaticallyServedFiles/APISpec/apiSpecification.json")
        self.api_spec = APISpecification(loads(api_spec_file.read_text()))

    @patch("application.use_case.event_use_cases.generate_prefixed_id")
    @patch("application.use_case.traveler_use_cases.generate_prefixed_id")
    @patch("application.use_case.location_use_cases.generate_prefixed_id")
    def test__api_route__should_return_expected_response__when_invoked(
            self,
            location_id_generator_mock: MagicMock, traveler_id_generator_mock: MagicMock, event_id_generator_mock: MagicMock,
    ) -> None:
        # Arrange
        location_id_generator_mock.side_effect = dummy_id_generator
        traveler_id_generator_mock.side_effect = dummy_id_generator
        event_id_generator_mock.side_effect = dummy_id_generator

        self.controller.profile = anon_profile()
        json_body = self.api_spec.get_resource_request_body_examples("/api/world/{worldId}/location", RESTMethod.POST) \
            .get("application/json")
        expected_response_bodies = self.api_spec.get_resource_response_body_examples("/api/world/{worldId}/location", RESTMethod.POST)

        # Act
        actual_status_code, actual_response_body = self.controller.invoke("/api/location", RESTMethod.POST, json=json_body)

        # Assert
        actual_status_code_str = str(actual_status_code.real)
        self.assertIn(actual_status_code_str, expected_response_bodies)
        expected_response_body = dumps(expected_response_bodies.get(actual_status_code_str).get("application/json"), indent=2)
        self.assertEqual(expected_response_body, actual_response_body)
