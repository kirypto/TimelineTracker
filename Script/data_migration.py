from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from distutils.version import StrictVersion
from json import loads
from logging import error, info
from pathlib import Path
from typing import Dict, NoReturn, Any, List, Tuple

from jsonpatch import JsonPatch, PatchOperation, InvalidJsonPatch
from ruamel.yaml import YAML

from util.logging import configure_logging


def _main() -> NoReturn:
    args = _parse_arguments()
    configure_logging()

    config: dict = YAML(typ="safe").load(Path(args.config))
    repository_config: Dict[str, str] = config["timeline_tracker_app_config"]["repositories_config"]
    from _version import __version__
    app_version = StrictVersion(__version__)
    _ensure_data_migrated_to_current_version(app_version, **repository_config)


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
            if version < data_version:
                continue
            info(f"Migrating data to version {version} ({change_description})")
            _apply_json_data_migration(json_repository_path, **instructions)
    exit(0)


def _apply_json_data_migration(
        json_repository_path: Path,
        *, location_modifications: List[Dict[str, Any]] = None, traveler_modifications: List[Dict[str, Any]] = None,
        event_modifications: List[Dict[str, Any]] = None,
        **kwargs
) -> None:
    valid_instructions = {"location_modifications", "traveler_modifications", "event_modifications"}
    if kwargs:
        error(f"Unknown json migration instructions. Must be subset of {valid_instructions}, but was: {set(kwargs.keys())}")
        exit(-1)
    if location_modifications:
        info("Apply modifications to Location entities")
        modification_patches = _validate_and_load_patch_instructions(location_modifications)
    if traveler_modifications:
        info("Apply modifications to Traveler entities")
        modification_patches = _validate_and_load_patch_instructions(traveler_modifications)
    if event_modifications:
        info("Apply modifications to Event entities")
        modification_patches = _validate_and_load_patch_instructions(event_modifications)


def _validate_and_load_patch_instructions(modifications: List[Dict[str, Any]]) -> JsonPatch:
    if not isinstance(modifications, list) or any([not isinstance(modification, dict) for modification in modifications]):
        error(f"Failed to load modification instructions, was not a valid JSON Patch: '{modifications}'")
        exit(-1)

    try:
        return JsonPatch([PatchOperation(operation).operation for operation in modifications])
    except InvalidJsonPatch as e:
        error(f"Failed to load modification instructions: {e}. Was '{modifications}'")
        exit(-1)


if __name__ == "__main__":
    _main()
