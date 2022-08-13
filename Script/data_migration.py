from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from distutils.version import StrictVersion
from logging import error, info, warning
from pathlib import Path
from subprocess import run
from typing import Dict, NoReturn, Any, List, Tuple, Union

from ruamel.yaml import YAML

from util.logging import configure_logging


_JsonMigration = Dict[str, Union[str, Dict[str, Any]]]
_UUID_MATCHER = "[0-9a-f]" * 8 + "-" + "[0-9a-f]" * 4 + "-" + "[1-5]" + "[0-9a-f]" * 3 + "-" + "[89ab]" + "[0-9a-f]" * 3 + "-" + \
                "[0-9a-f]" * 12


def _main() -> NoReturn:
    args = _parse_arguments()
    configure_logging()

    # noinspection PyBroadException
    try:
        config: dict = YAML(typ="safe").load(Path(args.config))
        repository_config: Dict[str, str] = config["timeline_tracker_app_config"]["repositories_config"]
        from _version import get_strict_version
        app_version = get_strict_version()
        _ensure_data_migrated_to_current_version(app_version, **repository_config)
    except Exception as e:
        error(f"Failure occurred during data migration: {e}", exc_info=e)
        exit(-1)


def _parse_arguments() -> Namespace:
    description = "Data Migration Tool: \n" \
                  " - Used to update repository data to newer versions.\n" \
                  " - The configuration file for the application will be read to determine repository type and location.\n" \
                  " - It is recommended to make a backup of your repository data before running this script against it."
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("-c", "--config", required=True,
                        help="Timeline Tracker API configuration file. Repository type/location are loaded from it")
    return parser.parse_args()


def _ensure_data_migrated_to_current_version(
        app_version: StrictVersion,
        *, world_repo_class_path: str = None, json_repositories_directory_root: str = None, **_) -> NoReturn:
    if world_repo_class_path == "adapter.persistence.in_memory_repositories.InMemoryWorldRepository":
        # No need to migrate data
        pass
    elif world_repo_class_path == "adapter.persistence.json_file_repositories.JsonFileWorldRepository":
        if json_repositories_directory_root is None:
            error("Config file specifies json type repositories but did not provide the directory root.")
            exit(-1)
        _ensure_json_data_migrated_to_current_version(app_version, json_repositories_directory_root)
    else:
        error(f"Failed to check data repository: unhandled repository type '{world_repo_class_path}'")
        exit(-1)


def _ensure_json_data_migrated_to_current_version(app_version: StrictVersion, json_repositories_directory_root: str) -> NoReturn:
    json_repository_path = Path(json_repositories_directory_root)
    data_version_file = json_repository_path.joinpath("repository_version.metadata")
    data_version = StrictVersion(data_version_file.read_text(encoding="utf8") if data_version_file.exists() else "0.0")
    if data_version > app_version:
        error("Repository data version is ahead of the application, this is an invalid state. Aborting...")
        exit(-1)

    if data_version == app_version:
        info("Repository data is already up to date with application version.")
    else:
        info(f"Migrating repository data from version {data_version} to version {app_version}")
        json_file_repository_migrations_dir = Path.cwd().joinpath("Source/Resources/DataMigrations/JsonFileRepositories")
        if not json_file_repository_migrations_dir.is_dir():
            error("Could not locate data migration files. (Was this script run from the Timeline Tracker API project root folder?)")
            exit(-1)

        migration_instructions: List[Tuple[StrictVersion, Path]] = sorted([
            (
                StrictVersion(migration_file.name.split("__")[0][1:]),
                migration_file
            )
            for migration_file in json_file_repository_migrations_dir.iterdir()
            if migration_file.name.endswith(".py")
        ])
        for version, migration_py_script in migration_instructions:
            if version <= data_version:
                continue
            if version > app_version:
                warning(f"A migration file exists for a version ({version}) greater than the application version {app_version}, ignoring.")
                continue

            _run_migration_script(json_repository_path, migration_py_script, version)
            _update_data_version_file(json_repository_path, version)

        _update_data_version_file(json_repository_path, app_version)
    exit(0)


def _run_migration_script(json_repository_path: Path, migration_py_script: Path, version: StrictVersion) -> None:
    migration_return_code = run(["python", migration_py_script.as_posix(), json_repository_path.as_posix()]).returncode
    if migration_return_code != 0:
        error(f"Failed to apply data migration to version {version}, non-zero return code (was {migration_return_code})")
        exit(-1)


def _update_data_version_file(json_repository_path: Path, version: StrictVersion) -> None:
    json_repository_path.joinpath("repository_version.metadata").write_text(str(version), encoding="utf8")
    info(f"Data has been migrated to version {version}")


if __name__ == "__main__":
    _main()
