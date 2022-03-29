from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.case import TestCase

from Test.Unittest.domain.persistence.test_repositories import TestLocationsRepository, TestTravelerRepository, TestEventRepository, \
    TestWorldsRepository
from adapter.persistence.json_file_repositories import JsonFileLocationRepository, JsonFileTravelerRepository, JsonFileEventRepository, \
    JsonFileWorldRepository
from domain.persistence.repositories import LocationRepository, TravelerRepository, EventRepository, WorldRepository


def _prepare_temp_directory_for_json_repo_tests() -> TemporaryDirectory:
    from _version import __version__

    repo_dir = TemporaryDirectory()
    Path(repo_dir.name).joinpath("repository_version.metadata").write_text(__version__)
    return repo_dir


class TestJsonFileWorldRepository(TestWorldsRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = _prepare_temp_directory_for_json_repo_tests()
        self._world_repository = JsonFileWorldRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> WorldRepository:
        return self._world_repository


class TestJsonFileLocationRepository(TestLocationsRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = _prepare_temp_directory_for_json_repo_tests()
        self._location_repository = JsonFileLocationRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> LocationRepository:
        return self._location_repository


class TestJsonFileTravelerRepository(TestTravelerRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = _prepare_temp_directory_for_json_repo_tests()
        self._location_repository = JsonFileTravelerRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> TravelerRepository:
        return self._location_repository


class TestJsonFileEventRepository(TestEventRepository, TestCase):
    def setUp(self) -> None:
        self._tmp_directory = _prepare_temp_directory_for_json_repo_tests()
        self._event_repository = JsonFileEventRepository(json_repositories_directory_root=self._tmp_directory.name)

    def tearDown(self) -> None:
        self._tmp_directory.cleanup()

    @property
    def repository(self) -> EventRepository:
        return self._event_repository
