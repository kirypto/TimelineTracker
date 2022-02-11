from pathlib import Path
from unittest import TestCase

from application.main import TimelineTrackerApp


class TestTimelineTrackerApp(TestCase):
    def test__init__should_initialize_app__when_config_provided(self) -> None:
        # Arrange
        config = {
            "repositories_config": {
                "repository_type": "memory",
            },
            "resources_folder_path": Path(__file__).parents[3].joinpath("Source/Resources/").resolve().as_posix(),
            "logging_config": {
                "disabled": True,
            },
        }

        # Act
        app = TimelineTrackerApp(**config)
        # TODO kirypto #99: Split these tests so the constructor and initialization of controllers are done separately
        app.initialize_controllers(rest_controller_config=dict(controller_class_path="unittest.mock.MagicMock"))

        # Assert
        self.assertIsNotNone(app.locations_request_handler)
        self.assertIsNotNone(app.travelers_request_handler)
        self.assertIsNotNone(app.event_request_handler)
