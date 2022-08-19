from unittest import TestCase
from unittest.mock import MagicMock

from Test.Unittest.test_helpers.anons import anon_anything, anon_name, anon_string
from adapter.auth.auth0 import setup_flask_auth
from util.logging import configure_logging


class TestAuth0(TestCase):
    _setup_flask_route_args: list
    _setup_flask_kwargs: dict

    @classmethod
    def setUpClass(cls) -> None:
        configure_logging(disabled=True)

    def setUp(self) -> None:
        self._setup_flask_route_args = [anon_name(), anon_name(), anon_name(), anon_name()]
        self._setup_flask_kwargs = {
            "auth_callback_route": anon_name(),
            "client_id": anon_string(),
            "domain": anon_name(),
            "api_audience": anon_string(),
            "algorithms": ["RS256"],
        }

    def test__setup_flask_auth__should_throw_exception__when_non_flask_type_given(self) -> None:
        # Arrange
        try:
            from flask import Flask
        except ModuleNotFoundError:
            self.skipTest("Flask tests are not applicable in this context")
            return
        invalid = anon_anything()

        # Act
        def action():
            setup_flask_auth(invalid, *self._setup_flask_route_args, **self._setup_flask_kwargs)

        # Assert
        self.assertRaises(TypeError, action)

    def test__setup_flask_auth__should_not_throw_exception__when_flask_type_given(self) -> None:
        # Arrange
        try:
            from flask import Flask
        except ModuleNotFoundError:
            self.skipTest("Flask tests are not applicable in this context")
            return
        flask_web_app = MagicMock(spec=Flask)
        flask_web_app.config = MagicMock()

        # Act
        setup_flask_auth(flask_web_app,  *self._setup_flask_route_args, **self._setup_flask_kwargs)

        # Assert
