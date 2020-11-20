from abc import ABC, abstractmethod
from typing import Callable, Any

from Test.Unittest.test_helpers.anons import anon_location, anon_anything, anon_traveler
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.persistence.repositories import LocationRepository, TravelerRepository
from domain.travelers import Traveler


class TestCrudRepository(ABC):
    assertIsNone: Callable
    assertEqual: Callable
    assertSetEqual: Callable
    assertRaises: Callable

    @property
    @abstractmethod
    def repository(self) -> Any:
        pass

    @abstractmethod
    def anon_entity(self) -> Any:
        pass

    @abstractmethod
    def get_entity_identifier(self, entity: Any) -> Any:
        pass

    def test__save__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = anon_anything(not_type=Location)

        # Act
        def Action(): self.repository.save(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__save__should_not_throw_exception__when_storing_valid_entity(self) -> None:
        # Arrange
        entity = self.anon_entity()

        # Act
        self.repository.save(entity)

        # Assert

    def test__retrieve__should_reject_invalid_types(self) -> None:
        # Arrange
        valid_type = type(self.get_entity_identifier(self.anon_entity()))
        invalid_type = anon_anything(not_type=valid_type)

        # Act
        def Action(): self.repository.retrieve(invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__retrieve__should_raise_exception__when_no_stored_entity_matches_the_given_identifier(self) -> None:
        # Arrange
        anon_identifier = self.get_entity_identifier(self.anon_entity())

        # Act
        def Action(): self.repository.retrieve(anon_identifier)

        # Assert
        self.assertRaises(NameError, Action)

    def test__retrieve__should_return_saved_entity__when_stored_entity_matches_the_given_identifier(self) -> None:
        # Arrange
        expected_entity = self.anon_entity()
        entity_identifier = self.get_entity_identifier(expected_entity)
        self.repository.save(expected_entity)

        # Act
        actual = self.repository.retrieve(entity_identifier)

        # Assert
        self.assertEqual(expected_entity, actual)

    def test__retrieve_all__should_return_empty_set__when_no_entities_stored(self) -> None:
        # Arrange
        expected = set()

        # Act
        actual = self.repository.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_stored_entities__when_entities_stored(self) -> None:
        # Arrange
        expected = {self.anon_entity(), self.anon_entity()}
        for entity in expected:
            self.repository.save(entity)

        # Act
        actual = self.repository.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)

    def test__delete__should_delete_entity__when_matching_entity_stored(self) -> None:
        # Arrange
        entity = self.anon_entity()
        entity_identifier = self.get_entity_identifier(entity)
        self.repository.save(entity)

        # Act
        self.repository.delete(entity_identifier)

        # Assert
        self.assertRaises(NameError, lambda: self.repository.retrieve(entity_identifier))

    def test__delete__should_raise_exception__when_no_matching_entity_stored(self) -> None:
        # Arrange
        anon_entity_identifier = self.get_entity_identifier(self.anon_entity())

        # Act
        def Action(): self.repository.delete(anon_entity_identifier)

        # Assert
        self.assertRaises(NameError, Action)


class TestLocationsRepository(TestCrudRepository):
    @property
    @abstractmethod
    def repository(self) -> LocationRepository:
        pass

    def anon_entity(self) -> Location:
        return anon_location()

    def get_entity_identifier(self, entity: Location) -> PrefixedUUID:
        return entity.id


class TestTravelerRepository(TestCrudRepository):
    @property
    @abstractmethod
    def repository(self) -> TravelerRepository:
        pass

    def anon_entity(self) -> Traveler:
        return anon_traveler()

    def get_entity_identifier(self, entity: Traveler) -> PrefixedUUID:
        return entity.id
