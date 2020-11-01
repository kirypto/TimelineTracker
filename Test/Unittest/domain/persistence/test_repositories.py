from abc import ABC, abstractmethod

from Test.Unittest.test_helpers.anons import anon_location
from domain.persistence.repositories import LocationRepository


class TestLocationsRepository(ABC):
    @property
    @abstractmethod
    def location_repository(self) -> LocationRepository:
        pass

    def test__save__should_not_throw_exception(self) -> None:
        # Arrange
        self.skipTest("Steel thread only")
        location = anon_location()

        # Act
        self.location_repository.save(location)

        # Assert
