from typing import Set
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_traveler, anon_location, anon_tag, anon_anything
from application.filtering_use_cases import FilteringUseCase
from domain.descriptors import NamedEntity
from domain.tags import TaggedEntity, Tag


class TestFilteringUseCase(TestCase):
    def test__filter_named_entity__should_pass_through_unused_kwargs(self) -> None:
        # Arrange

        # Act
        _, actual = FilteringUseCase.filter_named_entities(set(), other_kwarg=anon_anything())

        # Assert
        self.assertIn("other_kwarg", actual)

    def test__filter_named_entities__should_pass_through_all__when_no_filters_provided(self) -> None:
        # Arrange
        expected: Set[NamedEntity] = {anon_traveler(), anon_location()}

        # Act
        actual, _ = FilteringUseCase.filter_named_entities(expected)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_named_entity__should_filter_down_to_matching__when_name_is_provided(self) -> None:
        # Arrange
        expected: Set[NamedEntity] = {anon_traveler(name="name"), anon_location(name="name")}
        all_named_entities = {anon_location()}
        all_named_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_named_entities(all_named_entities, name_is="name")

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_named_entity__should_filter_down_to_matching__when_name_has_provided(self) -> None:
        # Arrange
        expected: Set[NamedEntity] = {anon_traveler(name="this name 1"), anon_location(name="that name 2")}
        all_named_entities = {anon_location()}
        all_named_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_named_entities(all_named_entities, name_has="name")

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_tagged_entity__should_pass_through_unused_kwargs(self) -> None:
        # Arrange

        # Act
        _, actual = FilteringUseCase.filter_tagged_entities(set(), other_kwarg=anon_anything())

        # Assert
        self.assertIn("other_kwarg", actual)

    def test__filter_tagged_entities__should_pass_through_all__when_no_filters_provided(self) -> None:
        # Arrange
        expected: Set[TaggedEntity] = {anon_traveler(), anon_location()}

        # Act
        actual, _ = FilteringUseCase.filter_tagged_entities(expected)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_tagged_entity__should_filter_down_to_matching__when_tagged_all_provided(self) -> None:
        # Arrange
        expected: Set[TaggedEntity] = {anon_traveler(tags={Tag("tag1"), Tag("tag2")}), anon_location(tags={Tag("tag1"), Tag("tag2"), anon_tag()})}
        all_tagged_entities = {anon_location(tags={Tag("tag1")})}
        all_tagged_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_tagged_entities(all_tagged_entities, tagged_all={Tag("tag1"), Tag("tag2")})

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_tagged_entity__should_filter_down_to_matching__when_tagged_any_provided(self) -> None:
        # Arrange
        expected: Set[TaggedEntity] = {anon_traveler(tags={Tag("tag1"), anon_tag()}), anon_location(tags={Tag("tag1"), anon_tag()})}
        all_tagged_entities = {anon_location(tags={anon_tag()})}
        all_tagged_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_tagged_entities(all_tagged_entities, tagged_any={Tag("tag1")})

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_tagged_entity__should_filter_down_to_matching__when_tagged_only_provided(self) -> None:
        # Arrange
        expected: Set[TaggedEntity] = {anon_traveler(tags={Tag("tag1")}), anon_location(tags=set())}
        all_tagged_entities = {anon_location(tags={Tag("tag1"), anon_tag()})}
        all_tagged_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_tagged_entities(all_tagged_entities, tagged_only={Tag("tag1")})

        # Assert
        self.assertEqual(expected, actual)
    
    def test__filter_tagged_entity__should_filter_down_to_matching__when_tagged_none_provided(self) -> None:
        # Arrange
        expected: Set[TaggedEntity] = {anon_traveler(tags={Tag("tag1"), anon_tag()}), anon_location(tags=set())}
        all_tagged_entities = {anon_location(tags={anon_tag(), Tag("tag2")})}
        all_tagged_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_tagged_entities(all_tagged_entities, tagged_none={Tag("tag2")})

        # Assert
        self.assertEqual(expected, actual)
