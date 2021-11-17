from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from distutils.version import StrictVersion
from glob import glob
from json import loads, dumps
from logging import error, info, warning
from pathlib import Path
from typing import Dict, NoReturn, Any, List, Tuple, Union

from jsonpatch import JsonPatch, PatchOperation, InvalidJsonPatch
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
        from _version import __version__
        app_version = StrictVersion(__version__)
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
        *, repository_type: str, json_repositories_directory_root: str = None) -> NoReturn:
    if repository_type == "json":
        if json_repositories_directory_root is None:
            error("Config file specifies json type repositories but did not provide the directory root.")
            exit(-1)
        _ensure_json_data_migrated_to_current_version(app_version, json_repositories_directory_root)
    else:
        error(f"Failed to check data repository: unhandled repository type '{repository_type}'")
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

        migration_instructions: List[Tuple[StrictVersion, str, Dict["str", Any]]] = sorted([
            (
                StrictVersion(migration_file.name.split("__")[0][1:]),
                migration_file.name.split("__")[1].removesuffix(".json").replace("_", " "),
                loads(migration_file.read_text(encoding="utf8"))
            )
            for migration_file in json_file_repository_migrations_dir.iterdir()
            if migration_file.name.endswith(".json")
        ])
        for version, change_description, instructions in migration_instructions:
            if version <= data_version:
                continue
            if version > app_version:
                warning(f"A migration file exists for a version ({version}) greater than the application version {app_version}, ignoring.")
                continue
            info(f"Attempting to migrate data to version {version} ({change_description})")
            _apply_json_data_migration(json_repository_path, **instructions)
            json_repository_path.joinpath("repository_version.metadata").write_text(str(version), encoding="utf8")
            info(f"Successfully migrated data to version {version}")

        json_repository_path.joinpath("repository_version.metadata").write_text(str(app_version), encoding="utf8")
        info(f"Successfully migrated data to version {app_version}")
    exit(0)


def _apply_json_data_migration(
        json_repository_path: Path,
        *, migrations: List[_JsonMigration] = None, warnings: List[str] = None, **kwargs
) -> None:
    valid_instructions = {"warnings", "migrations"}
    if not isinstance(migrations, list):
        error(f"Invalid json migration instructions. Must contain 'migrations' list.")
        exit(-1)
    if kwargs:
        error(f"Invalid json migration instructions. Must be subset of {valid_instructions}, but was: {set(kwargs.keys())}")
        exit(-1)

    if warnings:
        for warning_message in warnings:
            warning(warning_message)
        if "y" != input("    Continue with migration? (y/N) ").lower():
            info("Aborting as instructed by user.")
            exit(-1)
    migrated_data_by_path: Dict[str, Dict[str, Any]] = {}
    for migration in migrations:
        matching_files, json_patch = _load_json_migration(json_repository_path, **migration)
        for file_path in matching_files:
            if file_path.as_posix() in migrated_data_by_path:
                json_data = migrated_data_by_path[file_path.as_posix()]
                print(dumps(json_data, indent=2))
            else:
                json_data = loads(file_path.read_text(encoding="utf8"))
            mutated = json_patch.apply(json_data)
            migrated_data_by_path[file_path.as_posix()] = mutated
    for file_path_raw, data in migrated_data_by_path.items():
        Path(file_path_raw).write_text(dumps(data, indent=2), encoding="utf8")


def _load_json_migration(json_repository_path: Path, path_matcher: str, data_patch: List[Dict[str, Any]]) -> Tuple[List[Path], JsonPatch]:
    full_path_matcher = json_repository_path.joinpath(path_matcher.replace("<guid>", _UUID_MATCHER)).as_posix()
    matching_files = [Path(path).resolve() for path in glob(full_path_matcher, recursive=True)]
    json_patch = _validate_and_load_json_patch(data_patch)
    return matching_files, json_patch


def _validate_and_load_json_patch(raw_patch: List[Dict[str, Any]]) -> JsonPatch:
    if not isinstance(raw_patch, list) or any([not isinstance(modification, dict) for modification in raw_patch]):
        error(f"Failed to load modification instructions, was not a valid JSON Patch: '{raw_patch}'")
        exit(-1)

    try:
        return JsonPatch([PatchOperation(operation).operation for operation in raw_patch])
    except InvalidJsonPatch as e:
        error(f"Failed to load modification instructions: {e}. Was '{raw_patch}'")
        exit(-1)


if __name__ == "__main__":
    _main()
