from distutils.version import StrictVersion
from unittest import TestCase


class VersionTest(TestCase):
    """
    Meant to ensure that the current version in _version can be retrieved as a StrictVersion. This is used in data migration but not
    in the main project code, and thus is not caught by other tests.
    Main concerns are properly handling "alpha", "beta", and similar, as these are not supported by the library but are used by this
    project to align with SemanticVersioning.
    """

    @staticmethod
    def test__app_version__should_not_fail() -> None:
        # Arrange

        # Act
        pass

        # Assert

    def test__app_version__should_return_correct_type(self) -> None:
        # Arrange

        # Act
        from _version import APP_VERSION
        actual = type(APP_VERSION)

        # Assert
        self.assertIs(StrictVersion, actual)

    @staticmethod
    def test__app_version_raw__should_not_fail() -> None:
        # Arrange

        # Act
        pass

        # Assert

    def test__app_version_raw__should_return_correct_type(self) -> None:
        # Arrange

        # Act
        from _version import APP_VERSION_RAW
        actual = type(APP_VERSION_RAW)

        # Assert
        self.assertIs(str, actual)
