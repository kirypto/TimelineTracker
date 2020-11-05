from abc import ABC, abstractmethod
from typing import Callable

from Test.Unittest.test_helpers.anons import anon_location, anon_prefixed_id, anon_anything
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository


class TestLocationsRepository(ABC):
    assertIsNone: Callable
    assertEqual: Callable
    assertSetEqual: Callable
    assertRaises: Callable

    @property
    @abstractmethod
    def location_repository(self) -> LocationRepository:
        pass

    def test__save__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = anon_anything(not_type=Location)

        # Act
        def Action(): self.location_repository.save(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__save__should_not_throw_exception(self) -> None:
        # Arrange
        location = anon_location()

        # Act
        self.location_repository.save(location)

        # Assert

    def test__retrieve__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = anon_anything(not_type=PrefixedUUID)

        # Act
        def Action(): self.location_repository.retrieve(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__retrieve__should_return_none__when_no_stored_location_matches_the_given_id(self) -> None:
        # Arrange

        # Act
        actual = self.location_repository.retrieve(anon_prefixed_id())

        # Assert
        self.assertIsNone(actual)

    def test__retrieve__should_return_saved_location__when_stored_location_with_given_id_exists(self) -> None:
        # Arrange
        expected_location = anon_location()
        self.location_repository.save(expected_location)

        # Act
        actual = self.location_repository.retrieve(expected_location.id)

        # Assert
        self.assertEqual(expected_location, actual)

    def test__retrieve_all__should_return_empty_set__when_no_locations_stored(self) -> None:
        # Arrange
        expected = set()

        # Act
        actual = self.location_repository.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_stored__when_locations_stored(self) -> None:
        # Arrange
        location = anon_location()
        self.location_repository.save(location)
        expected = {location}

        # Act
        actual = self.location_repository.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)
