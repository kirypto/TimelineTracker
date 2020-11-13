from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_location
from adapter.request_handling.views import LocationView
from domain.locations import Location


class TestLocationView(TestCase):
    def test__to_json__should_translate_to_json_dict(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = LocationView.to_json(location)

        # Assert
        self.assertTrue(type(actual) is dict)

    def test__from_json__should_translate_from_json_dict(self) -> None:
        # Arrange
        location = anon_location()
        json = LocationView.to_json(location)

        # Act
        actual = Location(**LocationView.kwargs_from_json(json))

        # Assert
        self.assertEqual(location, actual)
