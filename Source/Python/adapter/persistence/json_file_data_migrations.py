from abc import ABC, abstractmethod
from distutils.version import StrictVersion
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Type, List, Tuple


_METADATA_VERSION_FILE = "repository_version.metadata"
_LOCATION_REPO_DIR_NAME = "LocationRepo"
_TRAVELER_REPO_DIR_NAME = "TravelerRepo"
_EVENT_REPO_DIR_NAME = "EventRepo"


class JsonDataMigrationScript(ABC):
    _repository_root_path: Path

    @property
    def repo_version_file(self) -> Path:
        return self._repository_root_path.joinpath(_METADATA_VERSION_FILE)

    @property
    def location_repo_dir(self) -> Path:
        return self._repository_root_path.joinpath(_LOCATION_REPO_DIR_NAME)

    @property
    def traveler_repo_dir(self) -> Path:
        return self._repository_root_path.joinpath(_TRAVELER_REPO_DIR_NAME)

    @property
    def event_repo_dir(self) -> Path:
        return self._repository_root_path.joinpath(_EVENT_REPO_DIR_NAME)

    @abstractmethod
    def __init__(self, repository_root_path: Path) -> None:
        self._repository_root_path = repository_root_path

    @staticmethod
    def get_migration_version_from_file(migration_script_file_name: str) -> StrictVersion:
        return StrictVersion(Path(migration_script_file_name).name.split("__")[0].removeprefix("v"))

    @abstractmethod
    def validate_safe_to_migrate(self) -> None:
        pass

    @abstractmethod
    def migrate_data(self) -> None:
        pass


class JsonFileDataMigrator:
    @classmethod
    def ensure_updated(cls, repository_root_path: Path) -> None:
        from application.main import AppInitializationData
        app_version = StrictVersion(AppInitializationData.get_version())
        migrations_folder = AppInitializationData.get_resources_folder().joinpath("DataMigrations/JsonFileRepositories")
        repository_version = cls._get_repository_version(repository_root_path)
        if repository_version > app_version:
            raise ValueError("Data stored in the configured Json File Repository is from a newer version of the app.\n"
                             f"Json data version: {repository_version}\nApplication version: {app_version}")

        if repository_version < app_version:
            cls._update_repository(repository_root_path, migrations_folder, app_version, repository_version)

    @classmethod
    def _get_repository_version(cls, repository_root_path: Path) -> StrictVersion:
        repository_version_file = repository_root_path.joinpath(_METADATA_VERSION_FILE)
        if not repository_version_file.exists() or not repository_version_file.is_file():
            raise ValueError(f"Could not locate {_METADATA_VERSION_FILE} in the repository root folder!\n"
                             f"(If upgrading from before v0.2.0, the file must be manually added, simply create it containing '0.1.3')")
        repository_version_str = repository_version_file.read_text("utf-8")
        if len(repository_version_str) == 0:
            raise ValueError(f"{_METADATA_VERSION_FILE} was empty")
        return StrictVersion(repository_version_str)

    @classmethod
    def _update_repository(
            cls, repository_root_path: Path, migrations_folder: Path, app_version: StrictVersion, repository_version: StrictVersion
    ) -> None:
        migration_scripts = cls._get_migration_scripts(migrations_folder)
        for version, migration_script in migration_scripts:
            if version <= repository_version:
                continue
            if version > app_version:
                raise ValueError(f"The Json migration script {migration_script.name} is for a version later than the application's version "
                                 f"({app_version})")
            cls._run_migration(migration_script, repository_root_path)

    @classmethod
    def _run_migration(cls, migration_script_path, repository_root_path):
        print(f"Applying Json File Repository data migration {migration_script_path.name}")
        try:
            spec = spec_from_file_location("version", migration_script_path.as_posix())
            migration_module = module_from_spec(spec)
            # noinspection PyUnresolvedReferences
            spec.loader.exec_module(migration_module)

            # noinspection PyUnresolvedReferences
            data_migration_class: Type[JsonDataMigrationScript] = migration_module.DataMigration

            migration_script = data_migration_class(repository_root_path)
            migration_script.validate_safe_to_migrate()
            migration_script.migrate_data()
        except Exception as e:
            raise RuntimeError(f"Failed to apply migration script {migration_script_path.name}: {str(e)}")

    @classmethod
    def _get_migration_scripts(cls, migrations_folder: Path) -> List[Tuple[StrictVersion, Path]]:
        migrations: List[Tuple[StrictVersion, Path]] = []
        for migration_script_path in migrations_folder.iterdir():
            if migration_script_path.suffix != ".py":
                continue
            version = StrictVersion(migration_script_path.name.split("__")[0].removeprefix("v"))
            migrations.append((version, migration_script_path))
        migrations.sort(key=lambda x: x[0])

        return migrations
