__version__ = "0.4.0"

from distutils.version import StrictVersion


def parse_version(raw_version: str) -> StrictVersion:
    compatible_version_string = raw_version.replace("alpha", "a").replace("beta", "b")
    return StrictVersion(compatible_version_string)


APP_VERSION_RAW = __version__
APP_VERSION = parse_version(APP_VERSION_RAW)
