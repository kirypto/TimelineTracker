from random import choices
from string import ascii_uppercase
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_location, anon_event, anon_traveler
from adapter.views import ValueTranslator
from domain.events import Event
from domain.locations import Location
from domain.tags import Tag
from domain.travelers import Traveler


class TestValueTranslator(TestCase):
    def test__from_json__should_convert_tags_to_lower_case(self) -> None:
        # Arrange
        uppercase_tag = ''.join(choices(ascii_uppercase, k=10))
        expected = uppercase_tag.lower()

        # Act
        tag = ValueTranslator.from_json(uppercase_tag, Tag)

        # Assert
        self.assertEqual(expected, str(tag))

    def test__from_json__should_convert_json_to_location(self) -> None:
        # Arrange
        location_json = ValueTranslator.to_json(anon_location())

        # Act
        location = ValueTranslator.from_json(location_json, Location)

        # Assert
        self.assertEqual(location_json["name"], location.name)
        self.assertEqual(location_json["description"], location.description)

    def test__from_json__should_convert_json_to_traveler(self) -> None:
        # Arrange
        traveler_json = ValueTranslator.to_json(anon_traveler())

        # Act
        traveler = ValueTranslator.from_json(traveler_json, Traveler)

        # Assert
        self.assertEqual(traveler_json["name"], traveler.name)
        self.assertEqual(traveler_json["description"], traveler.description)

    def test__from_json__should_convert_json_to_event(self) -> None:
        # Arrange
        event_json = ValueTranslator.to_json(anon_event())

        # Act
        event = ValueTranslator.from_json(event_json, Event)

        # Assert
        self.assertEqual(event_json["name"], event.name)
        self.assertEqual(event_json["description"], event.description)

    def test__to_json__should_translate_location_to_json_dict(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = ValueTranslator.to_json(location)

        # Assert
        self.assertTrue(type(actual) is dict)
        self.assertIn("id", actual)
        self.assertIn("name", actual)
        self.assertIn("description", actual)
        self.assertIn("span", actual)
        self.assertIn("tags", actual)
        self.assertIn("metadata", actual)

    def test__to_json__should_translate_traveler_to_json_dict(self) -> None:
        # Arrange
        traveler = anon_traveler()

        # Act
        actual = ValueTranslator.to_json(traveler)

        # Assert
        self.assertTrue(type(actual) is dict)
        self.assertIn("id", actual)
        self.assertIn("name", actual)
        self.assertIn("description", actual)
        self.assertIn("journey", actual)
        self.assertIn("tags", actual)
        self.assertIn("metadata", actual)

    def test__to_json__should_translate_event_to_json_dict(self) -> None:
        # Arrange
        event = anon_event()

        # Act
        actual = ValueTranslator.to_json(event)

        # Assert
        self.assertTrue(type(actual) is dict)
        self.assertIn("id", actual)
        self.assertIn("name", actual)
        self.assertIn("description", actual)
        self.assertIn("span", actual)
        self.assertIn("tags", actual)
        self.assertIn("metadata", actual)
