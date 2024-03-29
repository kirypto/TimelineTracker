from typing import Any, Optional

from flask import Flask
from flask.testing import FlaskClient
from flask_unittest import ClientTestCase

from Test.Unittest.test_application.requests.rest.test_controllers import TestRESTController
from Test.Unittest.test_helpers.anons import anon_string
from adapter.runners.flask_app import FlaskRESTController
from application.access.clients import Profile
from application.requests.rest import RESTMethod
from application.requests.rest.controllers import RESTController


def _create_flask_test_app() -> Flask:
    flask = Flask(__name__)
    flask.secret_key = anon_string()
    return flask


class TestFlaskRESTController(TestRESTController, ClientTestCase):
    app = _create_flask_test_app()
    _controller: RESTController
    _client: FlaskClient

    def setUp(self, client: FlaskClient) -> None:
        self._controller = FlaskRESTController(flask_web_app=self.app)
        self._client = client

        # TODO kirypto 2022-sept-03: Find a better way than modifying the private field. Currenly we need to manually reset the
        #  'got first request' boolean as Flask rejects adding new routes after a request is received. This is only an issue because the
        #  'app' field is initialized once on the class and reused for all tests. Created an issue in the flask_unittest repository to
        #  hopefully have this addressed: https://github.com/TotallyNotChase/flask-unittest/issues/7
        self.app._got_first_request = False

    def tearDown(self, client: FlaskClient) -> None:
        with client.session_transaction() as session:
            if "profile" in session:
                del session["profile"]

    @property
    def controller(self) -> RESTController:
        return self._controller

    def invoke(self, route: str, method: RESTMethod, *, json: Any = None, query_params: dict = None) -> Any:
        return self._client.open(route, method=method.value, json=json, query_string=query_params)

    def setup_equivalent_of_profile(self, profile: Optional[Profile]) -> None:
        with self._client.session_transaction() as session:
            if profile is None:
                if "profile" in session:
                    del session["profile"]
            else:
                session["profile"] = {"user_id": profile.user_id, "name": profile.name}
