from tempfile import TemporaryDirectory
from unittest.case import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository, TestTravelerRepository
from adapter.persistence.json_file_repositories import JsonFileLocationRepository, JsonFileTravelerRepository
from domain.persistence.repositories import LocationRepository, TravelerRepository


class TestJsonFileLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = TemporaryDirectory()
        self._location_repository = JsonFileLocationRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> LocationRepository:
        return self._location_repository


class TestJsonFileTravelerRepository(TestTravelerRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = TemporaryDirectory()
        self._location_repository = JsonFileTravelerRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> TravelerRepository:
        return self._location_repository
