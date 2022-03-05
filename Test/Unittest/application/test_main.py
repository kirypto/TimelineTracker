from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from application.main import TimelineTrackerApp


_CONFIG = {
    "repositories_config": {
        "repository_type": "memory",
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

    @patch("application.main.LocationsRestRequestHandler")
    def test__initialize_controllers__should_register_location_routes(self, location_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(rest_controller_config=dict(controller_class_path="unittest.mock.MagicMock"))

        # Assert
        location_route_registration_method: MagicMock = location_handler_class_mock.register_routes
        location_route_registration_method.assert_called_once()

    @patch("application.main.TravelersRestRequestHandler")
    def test__initialize_controllers__should_register_traveler_routes(self, traveler_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(rest_controller_config=dict(controller_class_path="unittest.mock.MagicMock"))

        # Assert
        traveler_route_registration_method: MagicMock = traveler_handler_class_mock.register_routes
        traveler_route_registration_method.assert_called_once()

    @patch("application.main.EventsRestRequestHandler")
    def test__initialize_controllers__should_register_event_routes(self, event_handler_class_mock: MagicMock) -> None:
        # Arrange
        app = TimelineTrackerApp(**_CONFIG)

        # Act
        app.initialize_controllers(rest_controller_config=dict(controller_class_path="unittest.mock.MagicMock"))

        # Assert
        event_route_registration_method: MagicMock = event_handler_class_mock.register_routes
        event_route_registration_method.assert_called_once()
