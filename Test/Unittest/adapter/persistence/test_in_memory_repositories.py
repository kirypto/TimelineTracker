from unittest import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository, TestTravelerRepository, TestEventRepository
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository, InMemoryEventRepository
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository


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


class TestInMemoryEventRepository(TestEventRepository, TestCase):
    def setUp(self) -> None:
        self._event_repository = InMemoryEventRepository()

    @property
    def repository(self) -> EventRepository:
        return self._event_repository
