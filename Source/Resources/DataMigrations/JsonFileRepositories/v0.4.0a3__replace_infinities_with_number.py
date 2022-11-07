from distutils.version import StrictVersion
from json import loads, dumps
from math import isinf
from pathlib import Path
from sys import argv, float_info
from typing import Any


__ver_and_descr = Path(__file__).name.removesuffix(".py")[1:].split("__")
new_version = StrictVersion(__ver_and_descr[0])
change_description = __ver_and_descr[1].replace("_", " ")
json_repository_path = Path(argv[1])
existing_version = StrictVersion(json_repository_path.joinpath("repository_version.metadata").read_text("utf8"))


def log(message: Any) -> None:
    print(f"[Migration v{new_version}] {message}")


log(f"Attempting to migrate data from v{existing_version} to v{new_version} ({change_description})")

FLOAT_MAX_VALUE = float_info.max
FLOAT_MIN_VALUE = -1 * FLOAT_MAX_VALUE

# Replace Infinity and -Infinity with FLOAT_MAX_VALUE and FLOAT_MIN_VALUE respectively
for path in list(json_repository_path.joinpath("LocationRepo").iterdir()) + list(json_repository_path.joinpath("EventRepo").iterdir()):
    json_data = loads(path.read_text("utf8"))
    for dimension in {"latitude", "longitude", "altitude", "continuum"}:
        for range_key in {"high", "low"}:
            value = json_data["span"][dimension][range_key]
            if isinf(value):
                replacement_value = FLOAT_MIN_VALUE if value < 0 else FLOAT_MAX_VALUE
                log(f"Replacing {path.name}'s span->{dimension}->{range_key} value of '{value}' with '{replacement_value}'")
                json_data["span"][dimension][range_key] = replacement_value
    path.write_text(dumps(json_data, indent=2), "utf8")
