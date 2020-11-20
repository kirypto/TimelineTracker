from unittest import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository, TestTravelerRepository
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository
from domain.persistence.repositories import LocationRepository, TravelerRepository


class TestInMemoryLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._location_repository = InMemoryLocationRepository()

    @property
    def repository(self) -> LocationRepository:
        return self._location_repository


class TestInMemoryTravelerRepository(TestTravelerRepository, TestCase):
    def setUp(self) -> None:
        self._traveler_repository = InMemoryTravelerRepository()

    @property
    def repository(self) -> TravelerRepository:
        return self._traveler_repository
