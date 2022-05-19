__version__ = "0.4.0alpha2"

from distutils.version import StrictVersion


def get_strict_version() -> StrictVersion:
    compatible_version_str = __version__.replace("alpha", "a").replace("beta", "b")
    return StrictVersion(compatible_version_str)
