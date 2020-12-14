from random import choices
from string import ascii_uppercase
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_location
from adapter.views import LocationView, ValueTranslator
from domain.locations import Location
from domain.tags import Tag


class TestValueTranslator(TestCase):
    def test__from_json__should_convert_tags_to_lower_case(self) -> None:
        # Arrange
        uppercase_tag = ''.join(choices(ascii_uppercase, k=10))
        expected = uppercase_tag.lower()

        # Act
        tag = ValueTranslator.from_json(uppercase_tag, Tag)

        # Assert
        self.assertEqual(expected, str(tag))


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
