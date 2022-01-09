from typing import Set
from unittest import TestCase
from unittest.mock import MagicMock

from Test.Unittest.test_helpers.anons import anon_anything
from application.requests.rest import RESTHandler, RouteDescriptor, RESTMethod, RESTController, RouteNotFoundError, RequestVerifier, \
    RequestHandler


class TestRESTController(TestCase):
    def test__init__should_throw_exception__when_multiple_handlers_register_the_same_route(self) -> None:
        # Arrange
        handler_1 = _RESTHandlerStub()
        handler_2 = _RESTHandlerStub()

        # Act
        def action(): RESTController({handler_1, handler_2})

        # Assert
        self.assertRaises(ValueError, action)

    def test__handle__should_throw_exception__when_route_is_not_supported(self) -> None:
        # Arrange
        handler = _RESTHandlerStub()
        rest_controller = RESTController({handler})

        # Act
        def action(): rest_controller.handle("/does/not/exist", RESTMethod.GET)

        # Assert
        self.assertRaises(RouteNotFoundError, action)

    def test__handle__should_throw_exception__when_method_is_not_supported(self) -> None:
        # Arrange
        handler = _RESTHandlerStub()
        rest_controller = RESTController({handler})

        # Act
        def action(): rest_controller.handle("/no/op", RESTMethod.POST)

        # Assert
        self.assertRaises(RouteNotFoundError, action)

    def test__handle__should_delegate_to_verifier__when_registered(self) -> None:
        # Arrange
        rest_handler = _RESTHandlerStub()
        request_verifier_mock = MagicMock()
        request_verifier_mock.return_value = (True, None)
        rest_handler.request_verifier = request_verifier_mock
        expected_args = {anon_anything(), anon_anything()}
        expected_kwargs = {"first": anon_anything(), "second": anon_anything()}
        rest_controller = RESTController({rest_handler})

        # Act
        rest_controller.handle("/no/op", RESTMethod.GET, *expected_args, **expected_kwargs)

        # Assert
        request_verifier_mock.assert_called_once_with(*expected_args, **expected_kwargs)

    def test__handle__should_throw_exception__when_verifier_returns_false(self) -> None:
        # Arrange
        rest_handler = _RESTHandlerStub()
        request_verifier_mock = MagicMock()
        request_verifier_mock.return_value = (False, "Nope!")
        rest_handler.request_verifier = request_verifier_mock
        rest_controller = RESTController({rest_handler})

        # Act
        def action(): rest_controller.handle("/no/op", RESTMethod.GET)

        # Assert
        self.assertRaises(ValueError, action)

    def test__handle__should_delegate_to_handler__when_registered(self) -> None:
        # Arrange
        rest_handler = _RESTHandlerStub()
        request_handler_mock = MagicMock()
        request_handler_mock.return_value = (200, {})
        rest_handler.request_handler = request_handler_mock
        expected_args = {anon_anything(), anon_anything()}
        expected_kwargs = {"first": anon_anything(), "second": anon_anything()}
        rest_controller = RESTController({rest_handler})

        # Act
        rest_controller.handle("/no/op", RESTMethod.GET, *expected_args, **expected_kwargs)

        # Assert
        request_handler_mock.assert_called_once_with(*expected_args, **expected_kwargs)

    def test__get_supported_routes__should_return_empty__when_none_specified(self) -> None:
        # Arrange
        rest_controller = RESTController(set())
        expected = set()

        # Act
        actual = rest_controller.get_supported_resources()

        # Assert
        self.assertEqual(expected, actual)

    def test__get_supported_routes__should_return_all_supported_routes__when_single_specified(self) -> None:
        # Arrange
        rest_handler = _RESTHandlerStub()
        rest_controller = RESTController({rest_handler})
        expected = {("/no/op", RESTMethod.GET)}

        # Act
        actual = rest_controller.get_supported_resources()

        # Assert
        self.assertEqual(expected, actual)

    def test__get_supported_routes__should_return_all_supported_routes__when_multiple_specified(self) -> None:
        # Arrange
        class _RESTHandlerStub2(RESTHandler):
            def get_routes(self) -> Set[RouteDescriptor]:
                no_op_put_descriptor: RouteDescriptor = "/no/op", RESTMethod.PUT, MagicMock(), MagicMock()
                hello_get_descriptor: RouteDescriptor = "/hello", RESTMethod.GET, MagicMock(), MagicMock()
                return {no_op_put_descriptor, hello_get_descriptor}

        rest_handler_1 = _RESTHandlerStub()
        rest_handler_2 = _RESTHandlerStub2()
        rest_controller = RESTController({rest_handler_1, rest_handler_2})
        expected = {("/no/op", RESTMethod.GET), ("/no/op", RESTMethod.PUT), ("/hello", RESTMethod.GET)}

        # Act
        actual = rest_controller.get_supported_resources()

        # Assert
        self.assertEqual(expected, actual)


class _RESTHandlerStub(RESTHandler):
    request_verifier: RequestVerifier
    request_handler: RequestHandler

    def __init__(self):
        verifier = MagicMock()
        verifier.return_value = (True, None)
        self.request_verifier = verifier
        handler = MagicMock()
        handler.return_value = (200, {})
        self.request_handler = handler

    def get_routes(self) -> Set[RouteDescriptor]:
        noop_descriptor: RouteDescriptor = "/no/op", RESTMethod.GET, self.request_verifier, self.request_handler
        return {
            noop_descriptor,
        }
