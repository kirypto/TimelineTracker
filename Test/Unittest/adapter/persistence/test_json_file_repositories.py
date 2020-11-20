from tempfile import TemporaryDirectory
from unittest.case import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository
from adapter.persistence.json_file_repositories import JsonFileLocationRepository
from domain.persistence.repositories import LocationRepository


class TestJsonFileLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = TemporaryDirectory()
        self._location_repository = JsonFileLocationRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> LocationRepository:
        return self._location_repository
