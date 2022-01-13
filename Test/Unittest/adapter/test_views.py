from copy import deepcopy
from random import choices
from string import ascii_uppercase
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_location, anon_event, anon_traveler, anon_tag, anon_int, anon_float
from application.requests.data_forms import JsonTranslator
from domain.collections import Range
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
        tag = JsonTranslator.from_json(uppercase_tag, Tag)

        # Assert
        self.assertEqual(expected, str(tag))

    def test__from_json__should_convert_json_to_location(self) -> None:
        # Arrange
        location_json = JsonTranslator.to_json(anon_location())

        # Act
        location = JsonTranslator.from_json(location_json, Location)

        # Assert
        self.assertEqual(location_json["name"], location.name)
        self.assertEqual(location_json["description"], location.description)

    def test__from_json__should_convert_json_to_traveler(self) -> None:
        # Arrange
        traveler_json = JsonTranslator.to_json(anon_traveler())

        # Act
        traveler = JsonTranslator.from_json(traveler_json, Traveler)

        # Assert
        self.assertEqual(traveler_json["name"], traveler.name)
        self.assertEqual(traveler_json["description"], traveler.description)

    def test__from_json__should_convert_json_to_event(self) -> None:
        # Arrange
        event_json = JsonTranslator.to_json(anon_event())

        # Act
        event = JsonTranslator.from_json(event_json, Event)

        # Assert
        self.assertEqual(event_json["name"], event.name)
        self.assertEqual(event_json["description"], event.description)

    def test__from_json__should_return_float_range_of_single_value__when_parsing_a_range_where_an_int_or_float_given(self) -> None:
        # Arrange
        value_1 = anon_int()
        value_2 = anon_float()
        expected_range_1 = Range(float(value_1), float(value_1))
        expected_range_2 = Range(value_2, value_2)

        # Act
        actual_1 = JsonTranslator.from_json(value_1, Range[float])
        actual_2 = JsonTranslator.from_json(value_2, Range[float])

        # Assert
        self.assertEqual(expected_range_1, actual_1)
        self.assertEqual(expected_range_2, actual_2)

    def test__to_json__should_translate_location_to_json_dict(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        actual = JsonTranslator.to_json(location)

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
        actual = JsonTranslator.to_json(traveler)

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
        actual = JsonTranslator.to_json(event)

        # Assert
        self.assertTrue(type(actual) is dict)
        self.assertIn("id", actual)
        self.assertIn("name", actual)
        self.assertIn("description", actual)
        self.assertIn("span", actual)
        self.assertIn("tags", actual)
        self.assertIn("metadata", actual)

    def test__to_json__should_return_sorted_list_of_string_tags__when_set_of_tags_given(self) -> None:
        # Arrange
        tags_1 = [anon_tag() for _ in range(100)]
        tags_2 = deepcopy(tags_1)
        tags_2.reverse()

        # Act
        actual_1 = JsonTranslator.to_json(set(tags_1))
        actual_2 = JsonTranslator.to_json(set(tags_2))

        # Assert
        self.assertListEqual(actual_1, actual_2)
