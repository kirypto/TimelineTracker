from unittest import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository
from domain.persistence.repositories import LocationRepository


class TestInMemoryLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._location_repository = LocationRepository()

    @property
    def location_repository(self) -> LocationRepository:
        return self._location_repository
