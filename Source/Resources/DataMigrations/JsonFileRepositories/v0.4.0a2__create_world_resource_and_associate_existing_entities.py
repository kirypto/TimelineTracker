from json import dumps
from pathlib import Path
from sys import argv
from typing import Any
from uuid import uuid4

from _version import parse_version
from application.requests.data_forms import JsonTranslator
from domain.ids import PrefixedUUID
from domain.worlds import World


__ver_and_descr = Path(__file__).name.removesuffix(".py")[1:].split("__")
new_version = parse_version(__ver_and_descr[0])
change_description = __ver_and_descr[1].replace("_", " ")
json_repository_path = Path(argv[1])
existing_version = parse_version(json_repository_path.joinpath("repository_version.metadata").read_text("utf8"))


def log(message: Any) -> None:
    print(f"[Migration v{new_version}] {message}")


if existing_version < parse_version("0.3.0"):
    log("[ERROR] This migration cannot be applied to data prior to v0.3.0. Please use the data migration tool from that version first, "
        "then run this version's again.")
    exit(-1)

log(f"Attempting to migrate data from v{existing_version} to v{new_version} ({change_description})")

# Generate a single world
world_repository_dir = json_repository_path.joinpath("WorldRepo")
world_repository_dir.mkdir(parents=True, exist_ok=True)
new_world_id = PrefixedUUID("world", uuid4())
new_world_json_path = world_repository_dir.joinpath(f"{new_world_id}.json")
world = World(
    id=new_world_id,
    name="World",
)
new_world_json_path.write_text(JsonTranslator.to_json_str(world), "utf8")
log(f"Generated a single new World resource with id {new_world_id}")

# Create location association index files
location_ids_to_associate = [
    path.name.removesuffix(".json")
    for path in json_repository_path.joinpath("LocationRepo").iterdir()
    if path.suffixes == [".json"]
]
world_repository_dir.joinpath("associated_locations.index").write_text(dumps({
    str(new_world_id): location_ids_to_associate
}))
log(f"Associated all existing locations with new world")

# Create traveler association index files
traveler_ids_to_associate = [
    path.name.removesuffix(".json")
    for path in json_repository_path.joinpath("TravelerRepo").iterdir()
    if path.suffixes == [".json"]
]
world_repository_dir.joinpath("associated_travelers.index").write_text(dumps({
    str(new_world_id): traveler_ids_to_associate
}))
log(f"Associated all existing travelers with new world")

# Create event association index files
event_ids_to_associate = [
    path.name.removesuffix(".json")
    for path in json_repository_path.joinpath("EventRepo").iterdir()
    if path.suffixes == [".json"]
]
world_repository_dir.joinpath("associated_events.index").write_text(dumps({
    str(new_world_id): event_ids_to_associate
}))
log(f"Associated all existing events with new world")

# Rename 'metadata' to 'attributes'
for path in json_repository_path.joinpath("LocationRepo").iterdir():
    path.write_text(path.read_text("utf8").replace('"metadata"', '"attributes"'), "utf8")
for path in json_repository_path.joinpath("TravelerRepo").iterdir():
    path.write_text(path.read_text("utf8").replace('"metadata"', '"attributes"'), "utf8")
for path in json_repository_path.joinpath("EventRepo").iterdir():
    path.write_text(path.read_text("utf8").replace('"metadata"', '"attributes"'), "utf8")
log(f"Renamed 'metadata' field to 'attributes' for all existing entities")
