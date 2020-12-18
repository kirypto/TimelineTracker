from typing import Set
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_traveler, anon_location, anon_tag, anon_anything
from application.filtering_use_cases import FilteringUseCase
from domain.collections import Range
from domain.descriptors import NamedEntity
from domain.positions import SpanningEntity, PositionalRange, Position, JourneyingEntity, PositionalMove, MovementType
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

    def test__filter_spanning_entity__should_pass_through_unused_kwargs(self) -> None:
        # Arrange

        # Act
        _, actual = FilteringUseCase.filter_spanning_entities(set(), other_kwarg=anon_anything())

        # Assert
        self.assertIn("other_kwarg", actual)

    def test__filter_spanning_entities__should_pass_through_all__when_no_filters_provided(self) -> None:
        # Arrange
        expected: Set[SpanningEntity] = {anon_location(), anon_location()}

        # Act
        actual, _ = FilteringUseCase.filter_spanning_entities(expected)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_spanning_entity__should_filter_down_to_matching__when_span_includes_provided(self) -> None:
        # Arrange
        positional_range = PositionalRange(latitude=Range(0, 1), longitude=Range(0, 1), altitude=Range(0, 1),
                                           continuum=Range(0, 1), reality=Range(0, 1))
        expected: Set[SpanningEntity] = {anon_location(span=positional_range)}
        all_spanning_entities = {anon_location()}
        all_spanning_entities |= expected
        position_filter = Position(latitude=0, longitude=0, altitude=0, continuum=0, reality=0)

        # Act
        actual, _ = FilteringUseCase.filter_spanning_entities(all_spanning_entities, span_includes=position_filter)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_spanning_entity__should_filter_down_to_matching__when_span_intersects_provided(self) -> None:
        # Arrange
        positional_range = PositionalRange(latitude=Range(0, 1), longitude=Range(0, 1), altitude=Range(0, 1),
                                           continuum=Range(0, 1), reality=Range(0, 1))
        expected: Set[SpanningEntity] = {anon_location(span=positional_range)}
        all_spanning_entities = {anon_location()}
        all_spanning_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_spanning_entities(all_spanning_entities, span_intersects=positional_range)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_journeying_entity__should_pass_through_unused_kwargs(self) -> None:
        # Arrange

        # Act
        _, actual = FilteringUseCase.filter_journeying_entities(set(), other_kwarg=anon_anything())

        # Assert
        self.assertIn("other_kwarg", actual)

    def test__filter_journeying_entities__should_pass_through_all__when_no_filters_provided(self) -> None:
        # Arrange
        expected: Set[JourneyingEntity] = {anon_traveler(), anon_traveler()}

        # Act
        actual, _ = FilteringUseCase.filter_journeying_entities(expected)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_journeying_entity__should_filter_down_to_matching__when_journey_includes_provided(self) -> None:
        # Arrange
        position = Position(latitude=0, longitude=0, altitude=0, continuum=0, reality=0)
        expected: Set[JourneyingEntity] = {anon_traveler(journey=[PositionalMove(position=position, movement_type=MovementType.IMMEDIATE)])}
        all_journeying_entities = {anon_traveler()}
        all_journeying_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_journeying_entities(all_journeying_entities, journey_includes=position)

        # Assert
        self.assertEqual(expected, actual)

    def test__filter_journeying_entity__should_filter_down_to_matching__when_journey_intersects_provided(self) -> None:
        # Arrange
        positional_range = PositionalRange(latitude=Range(0, 1), longitude=Range(0, 1), altitude=Range(0, 1),
                                           continuum=Range(0, 1), reality=Range(0, 1))
        position = Position(latitude=0, longitude=0, altitude=0, continuum=0, reality=0)
        expected: Set[JourneyingEntity] = {anon_traveler(journey=[PositionalMove(position=position, movement_type=MovementType.IMMEDIATE)])}
        all_journeying_entities = {anon_traveler()}
        all_journeying_entities |= expected

        # Act
        actual, _ = FilteringUseCase.filter_journeying_entities(all_journeying_entities, journey_intersects=positional_range)

        # Assert
        self.assertEqual(expected, actual)
