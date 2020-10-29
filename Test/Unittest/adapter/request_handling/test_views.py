from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_location
from adapter.request_handling.views import LocationView


class TestLocationView(TestCase):
    def test__to_json__should_translate_to_json_dict(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = LocationView.to_json_dict(location)

        # Assert
        self.assertTrue(type(actual) is dict)

    def test__from_json__should_translate_from_json_dict(self) -> None:
        # Arrange
        location = anon_location()
        json = LocationView.to_json_dict(location)

        # Act
        actual = LocationView.from_json(json)

        # Assert
        self.assertEqual(location, actual)

