from http import HTTPStatus
from json import loads, dumps
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import UUID

from parameterized import parameterized

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


def _dummy_id_generator(prefix: str) -> PrefixedUUID:
    return PrefixedUUID(prefix, UUID("abad1dea-0000-4000-8000-000000000000"))


def _get_api_spec() -> APISpecification:
    api_spec_file = Path(__file__).parents[4].joinpath("Source/Resources/StaticallyServedFiles/APISpec/apiSpecification.json")
    return APISpecification(loads(api_spec_file.read_text()))


def _get_test_params() -> List[Tuple[str, RESTMethod]]:
    api_spec = _get_api_spec()
    test_params: List[Tuple[str, RESTMethod]] = []
    for route, methods in api_spec.get_resources().items():
        for method in methods:
            test_params.append((route, method))
    return test_params


class TestAPISpecification(TestCase):
    api_spec: APISpecification = _get_api_spec()
    controller: TestableRESTController

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

    @parameterized.expand(_get_test_params())
    @patch("application.use_case.event_use_cases.generate_prefixed_id")
    @patch("application.use_case.traveler_use_cases.generate_prefixed_id")
    @patch("application.use_case.location_use_cases.generate_prefixed_id")
    @patch("application.use_case.world_use_cases.generate_prefixed_id")
    def test__api_route__(
            self,
            route, method, world_id_generator_mock: MagicMock, location_id_generator_mock: MagicMock,
            traveler_id_generator_mock: MagicMock, event_id_generator_mock: MagicMock,
    ) -> None:
        # Arrange
        world_id_generator_mock.side_effect = _dummy_id_generator
        location_id_generator_mock.side_effect = _dummy_id_generator
        traveler_id_generator_mock.side_effect = _dummy_id_generator
        event_id_generator_mock.side_effect = _dummy_id_generator

        self.controller.profile = anon_profile()
        json_body = self.api_spec.get_resource_request_body_examples(route, method).get("test_application/json")
        expected_response_bodies = self.api_spec.get_resource_response_body_examples(route, method)

        # Act
        actual_status_code, actual_response_body = self.controller.invoke(route, method, json=json_body)

        # Assert
        self.assertNotEqual(HTTPStatus.NOT_FOUND, actual_status_code, f"Resource {method} {route} not registered")
        self.assertNotEqual(HTTPStatus.METHOD_NOT_ALLOWED, actual_status_code, f"Resource {method} {route} not registered")
        self.assertNotEqual(HTTPStatus.NOT_IMPLEMENTED, actual_status_code, f"Resource {method} {route} has not been implemented")
        actual_status_code_str = str(actual_status_code.real)
        self.assertIn(actual_status_code_str, expected_response_bodies)
        expected_response_body = dumps(expected_response_bodies.get(actual_status_code_str).get("test_application/json"), indent=2)
        self.assertEqual(expected_response_body, actual_response_body)
