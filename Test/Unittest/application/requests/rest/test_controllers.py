from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Callable, Any, Optional

from Test.Unittest.test_helpers.anons import anon_string, anon_name, anon_route
from application.access.clients import Profile
from application.requests.rest import RESTMethod, HandlerResult
from application.requests.rest.controllers import RESTController
from application.requests.rest.utils import error_response


class TestRESTController(ABC):
    assertIsNone: Callable
    assertEqual: Callable
    fail: Callable

    @property
    @abstractmethod
    def controller(self) -> RESTController:
        pass

    @abstractmethod
    def invoke(self, route: str, method: RESTMethod, *, json: Any = None, query_params: dict = None) -> Any:
        pass

    @abstractmethod
    def setup_equivalent_of_profile(self, profile: Optional[Profile]) -> None:
        pass

    def test__registered_route__should_return_error_response__when_exception_thrown(self, *_) -> None:
        # Arrange
        expected_json, expected_status_code = error_response("expected message", HTTPStatus.BAD_REQUEST)
        route = anon_route()

        @self.controller.register_rest_endpoint(route, RESTMethod.GET)
        def handler(**_):
            # Act
            raise ValueError("expected message")

        actual = self.invoke(route, RESTMethod.GET)

        # Assert
        self.assertEqual(expected_status_code, actual.status_code)
        self.assertEqual(expected_json, actual.json)

    def test__registered_route__should_pass_none_for_profile__when_profile_equivalent_not_set(self, *_) -> None:
        # Arrange
        self.setup_equivalent_of_profile(None)
        route = anon_route()

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET)
        def handler(*, profile: Profile = None, **_) -> HandlerResult:
            # Assert
            self.assertIsNone(profile)
            return HTTPStatus.OK, ""

        self.invoke(route, RESTMethod.GET)

    def test__registered_route__should_pass_expected_profile__when_profile_equivalent_is_set(self, *_) -> None:
        # Arrange
        expected = Profile(anon_string(), anon_name())
        self.setup_equivalent_of_profile(expected)
        route = anon_route()

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET)
        def handler(*, profile: Profile = None, **_):
            # Assert
            self.assertEqual(expected, profile)

        self.invoke(route, RESTMethod.GET)

    def test__registered_route__should_not_pass_body__when_body_not_requested(self, *_) -> None:
        # Arrange
        route = anon_route()

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET, json=False)
        def handler(*args, **_) -> None:
            # Assert
            self.assertEqual(0, len(args))

        self.invoke(route, RESTMethod.GET, json=None)

    def test__registered_route__should_pass_body__when_body_requested_and_available(self, *_) -> None:
        # Arrange
        route = anon_route()
        expected_body = anon_string()

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET, json=True)
        def handler(json_body: Any, **_) -> None:
            # Assert
            self.assertEqual(expected_body, json_body)

        self.invoke(route, RESTMethod.GET, json=expected_body)

    def test__registered_route__should_return_error_response__when_body_requested_but_not_available(self, *_) -> None:
        # Arrange
        route = anon_route()
        expected_json, expected_status_code = error_response("Json body must be provided", HTTPStatus.BAD_REQUEST)

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET, json=True)
        def handler(body: Any, **_) -> None:
            self.fail(f"Should not have invoked method as 'body' arg should not have been passed in, was {body}")

        actual = self.invoke(route, RESTMethod.GET, json=None)

        # Assert
        self.assertEqual(expected_status_code, actual.status_code)
        self.assertEqual(expected_json, actual.json)
