from distutils.version import StrictVersion
from unittest import TestCase

from _version import get_strict_version


class VersionTest(TestCase):
    """
    Meant to ensure that the current version in _version can be retrieved as a StrictVersion. This is used in data migration but not
    in the main project code, and thus is not caught by other tests.
    Main concerns are properly handling "alpha", "beta", and similar, as these are not supported by the library but are used by this
    project to align with SemanticVersioning.
    """

    @staticmethod
    def test__get_strict_version__should_not_fail() -> None:
        # Arrange

        # Act
        get_strict_version()

        # Assert

    def test__get_strict_version__should_return_correct_type(self) -> None:
        # Arrange

        # Act
        actual = type(get_strict_version())

        # Assert
        self.assertIs(StrictVersion, actual)
