from unittest import TestCase

from application.main import TimelineTrackerApp


class TestTimelineTrackerApp(TestCase):
    def test__init__should_initialize_app__when_config_provided(self) -> None:
        # Arrange
        config = {
            "repositories_config": {
                "repository_type": "memory"
            },
            "request_handlers_config": {
                "request_handler_type": "rest"
            },
        }

        # Act
        app = TimelineTrackerApp(**config)

        # Assert
        self.assertIsNotNone(app.locations_request_handler)
        self.assertIsNotNone(app.travelers_request_handler)
        self.assertIsNotNone(app.event_request_handler)
