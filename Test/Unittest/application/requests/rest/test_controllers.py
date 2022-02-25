from abc import ABC, abstractmethod
from http import HTTPStatus
from random import choice
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
    assertRaises: Callable

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

    def fail_with_message(self, message: str) -> HandlerResult:
        # Return HandlerResult to pass method validation
        self.fail(message)
        # noinspection PyUnreachableCode
        return HTTPStatus.OK, ""

    def test__registered_route__should_return_error_response__when_exception_thrown(self, *_) -> None:
        # Arrange
        expected_json, expected_status_code = error_response("expected message", HTTPStatus.BAD_REQUEST)
        route = anon_route()

        @self.controller.register_rest_endpoint(route, RESTMethod.GET)
        def handler(**_) -> HandlerResult:
            # Act
            raise ValueError("expected message")

        self.controller.finalize()
        actual = self.invoke(route, RESTMethod.GET)

        # Assert
        self.assertEqual(expected_status_code, actual.status_code)
        self.assertEqual(expected_json, actual.json)

    def test__registered_route__should_delegate_to_correct_handler__when_route_registered_with_multiple_methods(self, *_) -> None:
        # Arrange
        route = anon_route()
        method_1 = choice(list(RESTMethod))
        method_2 = choice([m for m in RESTMethod if m != method_1])
        expected_1, expected_2 = anon_string(), anon_string()

        # Act
        @self.controller.register_rest_endpoint(route, method_1)
        def handler_1(**_) -> HandlerResult:
            return HTTPStatus.OK, expected_1

        @self.controller.register_rest_endpoint(route, method_2)
        def handler_2(**_) -> HandlerResult:
            return HTTPStatus.OK, expected_2

        self.controller.finalize()
        actual_1 = self.invoke(route, method_1)
        actual_2 = self.invoke(route, method_2)

        # Assert
        self.assertEqual(expected_1, actual_1.data.decode())
        self.assertEqual(expected_2, actual_2.data.decode())

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
        def handler(*, profile: Profile = None, **_) -> HandlerResult:
            # Assert
            self.assertEqual(expected, profile)
            return HTTPStatus.OK, ""

        self.invoke(route, RESTMethod.GET)

    def test__registered_route__should_not_pass_body__when_body_not_requested(self, *_) -> None:
        # Arrange
        route = anon_route()

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET, json=False)
        def handler(*args, **_) -> HandlerResult:
            # Assert
            self.assertEqual(0, len(args))
            return HTTPStatus.OK, ""

        self.invoke(route, RESTMethod.GET, json=None)

    def test__registered_route__should_pass_body__when_body_requested_and_available(self, *_) -> None:
        # Arrange
        route = anon_route()
        expected_body = anon_string()

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET, json=True)
        def handler(json_body: Any, **_) -> HandlerResult:
            # Assert
            self.assertEqual(expected_body, json_body)
            return HTTPStatus.OK, ""

        self.invoke(route, RESTMethod.GET, json=expected_body)

    def test__registered_route__should_return_error_response__when_body_requested_but_not_available(self, *_) -> None:
        # Arrange
        route = anon_route()
        expected_json, expected_status_code = error_response("Json body must be provided", HTTPStatus.BAD_REQUEST)

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET, json=True)
        def handler(body: Any, **_) -> HandlerResult:
            return self.fail_with_message(f"Should not have invoked method as 'body' arg should not have been passed in, was {body}")

        self.controller.finalize()

        actual = self.invoke(route, RESTMethod.GET, json=None)

        # Assert
        self.assertEqual(expected_status_code, actual.status_code)
        self.assertEqual(expected_json, actual.json)

    def test__register_route__should_throw_exception__when_controller_already_finalized(self, *_) -> None:
        # Arrange
        self.controller.finalize()

        # Act
        def action():
            @self.controller.register_rest_endpoint(anon_route(), RESTMethod.GET)
            def handler(**_) -> HandlerResult:
                return self.fail_with_message("Should not make it here")

        # Assert
        self.assertRaises(ValueError, action)

    def test__finalize__should_throw_exception__when_already_finalized(self, *_) -> None:
        # Arrange
        self.controller.finalize()

        # Act
        def action():
            self.controller.finalize()

        # Assert
        self.assertRaises(ValueError, action)

    def test__registered_routes__should_not_be_active__when_not_yet_finalized(self, *_) -> None:
        # Arrange
        route = anon_route()

        @self.controller.register_rest_endpoint(route, RESTMethod.GET)
        def handler(**_) -> HandlerResult:
            return self.fail_with_message("Should not make it here")

        # Act
        actual = self.invoke(route, RESTMethod.GET)

        # Assert
        self.assertEqual(HTTPStatus.NOT_FOUND, actual.status_code)
    
    def test__register_rest_endpoint__should_raise_exception__when_handler_does_not_accept_correct_arguments(self, *_) -> None:
        # Arrange
        route = anon_route() + "/<foo>" + anon_route() + "/<bar>"

        # Act
        def action():
            @self.controller.register_rest_endpoint(route, RESTMethod.GET)
            def handler() -> HandlerResult:
                return self.fail_with_message(f"Should not make it here.")

        # Assert
        self.assertRaises(ValueError, action)

    def test__register_rest_endpoint__should_raise_exception__when_handler_has_url_params_as_non_keyword_only_arguments(self, *_) -> None:
        # Arrange
        route = anon_route() + "/<foo>" + anon_route() + "/<bar>"

        # Act
        def action():
            @self.controller.register_rest_endpoint(route, RESTMethod.GET)
            def handler(foo, bar) -> HandlerResult:
                return self.fail_with_message(f"Should not make it here. (prevent unused warnings: {foo}, {bar})")

        # Assert
        self.assertRaises(ValueError, action)

    def test__register_rest_endpoint__should_not_raise_exception__when_handler_has_keyword_only_arguments_for_each_url_param(
            self, *_
    ) -> None:
        # Arrange
        route = anon_route() + "/<foo>" + anon_route() + "/<bar>"

        # Act
        @self.controller.register_rest_endpoint(route, RESTMethod.GET)
        def handler(*, foo, bar) -> HandlerResult:
            return self.fail_with_message(f"Should not make it here. (prevent unused warnings: {foo}, {bar})")

        # Assert
