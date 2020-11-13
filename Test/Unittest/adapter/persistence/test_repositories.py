from unittest import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository
from adapter.persistence.repositories import InMemoryLocationRepository, JsonFileLocationRepository
from domain.persistence.repositories import LocationRepository


class TestInMemoryLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._location_repository = InMemoryLocationRepository()

    @property
    def location_repository(self) -> LocationRepository:
        return self._location_repository


class TestJsonFileLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._location_repository = JsonFileLocationRepository()

    @property
    def location_repository(self) -> LocationRepository:
        return self._location_repository
