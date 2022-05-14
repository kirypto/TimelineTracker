from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from adapter.persistence.in_memory_repositories import InMemoryEventRepository, InMemoryTravelerRepository, InMemoryLocationRepository, \
    InMemoryWorldRepository
from application.main import TimelineTrackerApp
from application.requests.rest import RESTMethod, MIMEType
from application.requests.rest.controllers import RESTController, HandlerRegisterer
from test_helpers import get_fully_qualified_name


_CONFIG = {
    "repositories_config": {
        "world_repo_class_path": get_fully_qualified_name(InMemoryWorldRepository),
        "location_repo_class_path": get_fully_qualified_name(InMemoryLocationRepository),
        "traveler_repo_class_path": get_fully_qualified_name(InMemoryTravelerRepository),
        "event_repo_class_path": get_fully_qualified_name(InMemoryEventRepository),
    },
    "resources_folder_path": Path(__file__).parents[3].joinpath("Source/Resources/").resolve().as_posix(),
    "logging_config": {
        "disabled": True,
    },
}


class TestTimelineTrackerApp(TestCase):
    def test__init__should_initialize_app__when_config_provided(self) -> None:
        # Arrange
        # Act
        app = TimelineTrackerApp(**_CONFIG)

        # Assert
        self.assertIsNotNone(app._location_use_case)
        self.assertIsNotNone(app._traveler_use_case)
        self.assertIsNotNone(app._event_use_case)
        self.assertIsNotNone(app._timeline_use_case)

    @patch("application.main.WorldsRESTRequestHandler")
    def test__initialize_controllers__should_register_world_routes(self, world_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(
            rest_controller_config=dict(controller_class_path="test_application.test_main.TestableRESTControllerStub"))

        # Assert
        world_route_registration_method: MagicMock = world_handler_class_mock.register_routes
        world_route_registration_method.assert_called_once()

    @patch("application.main.LocationsRestRequestHandler")
    def test__initialize_controllers__should_register_location_routes(self, location_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(
            rest_controller_config=dict(controller_class_path="test_application.test_main.TestableRESTControllerStub"))

        # Assert
        location_route_registration_method: MagicMock = location_handler_class_mock.register_routes
        location_route_registration_method.assert_called_once()

    @patch("application.main.TravelersRestRequestHandler")
    def test__initialize_controllers__should_register_traveler_routes(self, traveler_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(
            rest_controller_config=dict(controller_class_path="test_application.test_main.TestableRESTControllerStub"))

        # Assert
        traveler_route_registration_method: MagicMock = traveler_handler_class_mock.register_routes
        traveler_route_registration_method.assert_called_once()

    @patch("application.main.EventsRestRequestHandler")
    def test__initialize_controllers__should_register_event_routes(self, event_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(
            rest_controller_config=dict(controller_class_path="test_application.test_main.TestableRESTControllerStub"))

        # Assert
        event_route_registration_method: MagicMock = event_handler_class_mock.register_routes
        event_route_registration_method.assert_called_once()


class TestableRESTControllerStub(RESTController):
    def register_rest_endpoint(
            self, route: str, method: RESTMethod, response_type: MIMEType = MIMEType.JSON, *, json: bool = False, query_params: bool = False
    ) -> HandlerRegisterer:
        return MagicMock()

    def finalize(self) -> None:
        pass
