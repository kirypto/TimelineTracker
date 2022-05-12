from json import loads, dumps
from pathlib import Path
from re import findall, compile as compile_pattern
from typing import List, Tuple, Optional, Dict
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import UUID

from inflection import underscore
from parameterized import parameterized

from adapter.persistence.in_memory_repositories import InMemoryEventRepository, InMemoryTravelerRepository, InMemoryLocationRepository, \
    InMemoryWorldRepository
from application.main import TimelineTrackerApp
from application.requests.rest import RESTMethod
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from application.use_case.world_use_cases import WorldUseCase
from domain.collections import Range
from domain.ids import PrefixedUUID
from domain.positions import PositionalRange, PositionalMove, MovementType, Position
from domain.tags import Tag
from test_helpers import get_fully_qualified_name
from test_helpers.anons import anon_profile, anon_name, anon_create_traveler_kwargs, anon_create_location_kwargs, anon_create_event_kwargs
from test_helpers.controllers import TestableRESTController
from test_helpers.specifications import APISpecification, StatusCode, ContentType, JSONObject


_CONFIG = {
    "resources_folder_path": Path(__file__).parents[4].joinpath("Source/Resources"),
    "repositories_config": {
        "world_repo_class_path": get_fully_qualified_name(InMemoryWorldRepository),
        "location_repo_class_path": get_fully_qualified_name(InMemoryLocationRepository),
        "traveler_repo_class_path": get_fully_qualified_name(InMemoryTravelerRepository),
        "event_repo_class_path": get_fully_qualified_name(InMemoryEventRepository),
    },
}
_OPENAPI_URL_PARAM_PATTERN = compile_pattern(r"{\w+}")


def _dummy_id_generator(prefix: str) -> PrefixedUUID:
    return PrefixedUUID(prefix, UUID("abad1dea-0000-4000-8000-000000000000"))


def _get_api_spec() -> APISpecification:
    api_spec_file = Path(__file__).parents[4].joinpath("Source/Resources/StaticallyServedFiles/APISpec/apiSpecification.json")
    return APISpecification(loads(api_spec_file.read_text()))


def _get_test_params() -> List[Tuple[str, str, RESTMethod]]:
    api_spec = _get_api_spec()
    test_params: List[Tuple[str, str, RESTMethod]] = []
    for route, methods in api_spec.get_resources().items():
        for method in methods:
            test_params.append((f"{method} {route}", route, method))
    return test_params


def _correct_url_params(route: str) -> str:
    translated_route = route
    openapi_url_params = findall(_OPENAPI_URL_PARAM_PATTERN, route)
    for openapi_param in openapi_url_params:
        converted_param = f"<{underscore(openapi_param[1:-1])}>"
        translated_route = translated_route.replace(openapi_param, converted_param, 1)
    return translated_route


def _extract_response_body(
        status_code: StatusCode, content_type: ContentType, response_bodies: Dict[StatusCode, Dict[ContentType, JSONObject]]
) -> str:
    response_bodies_by_content_type = response_bodies[status_code]
    if content_type in response_bodies_by_content_type:
        body = response_bodies_by_content_type[content_type]
    elif "*/*" in response_bodies_by_content_type:
        body = response_bodies_by_content_type["*/*"]
    else:
        raise KeyError(f"{content_type} not in known responses")

    return body if type(body) is str else dumps(body, indent=2)


class TestAPISpecification(TestCase):
    api_spec: APISpecification = _get_api_spec()
    controller: TestableRESTController
    world_use_case: WorldUseCase
    location_use_case: LocationUseCase
    traveler_use_case: TravelerUseCase
    event_use_case: EventUseCase

    @patch("application.main.RESTControllersFactory")
    def setUp(
            self, rest_controller_factory_class_mock: MagicMock,
    ) -> None:
        self.controller = TestableRESTController()
        timeline_tracker_application = TimelineTrackerApp(**_CONFIG)
        self.world_use_case = timeline_tracker_application._world_use_case
        self.location_use_case = timeline_tracker_application._location_use_case
        self.traveler_use_case = timeline_tracker_application._traveler_use_case
        self.event_use_case = timeline_tracker_application._event_use_case

        def rest_controller_factory(**_):
            factory_result = MagicMock()  # Container to store rest_controller property
            factory_result.rest_controller = self.controller
            return factory_result

        rest_controller_factory_class_mock.side_effect = rest_controller_factory

        timeline_tracker_application.initialize_controllers(rest_controller_config={})

        api_spec_file = Path(__file__).parents[4].joinpath("Source/Resources/StaticallyServedFiles/APISpec/apiSpecification.json")
        self.api_spec = APISpecification(loads(api_spec_file.read_text()))
        self.controller.profile = anon_profile()

    def _set_up_for(self, route: str, method: RESTMethod) -> Optional[Dict[str, str]]:
        url_params: Dict[str, str] = {}
        tags = {Tag("important")}
        range_ = Range(-5.1, 15.1)
        span = PositionalRange(latitude=range_, longitude=range_, altitude=range_, continuum=range_, reality={0})
        position = Position(latitude=-5.05, longitude=-2.6, altitude=3.5, continuum=11.9, reality=0)
        journey = [PositionalMove(position=position, movement_type=MovementType.IMMEDIATE)]
        attributes = {"key1": "Value A", "key2": "Value B"}
        profile = self.controller.profile

        if route.startswith("/api/world/{worldId}/"):
            world = self.world_use_case.create(name=anon_name(), profile=profile)
            url_params["world_id"] = str(world.id)
        else:
            world = None

        if route == "/api/worlds" and method == RESTMethod.GET:
            self.world_use_case.create(name="The Great Pyramid", tags=tags, profile=profile)
        elif route == "/api/world/{worldId}" and method in {RESTMethod.DELETE, RESTMethod.GET, RESTMethod.PATCH}:
            world = self.world_use_case.create(
                name="The Milky Way", tags=tags, attributes=attributes,
                description="The Milky Way is the galaxy that includes our Solar System, with the name describing the galaxy's appearance "
                            "from Earth.\n",
                profile=profile)
            url_params["world_id"] = str(world.id)
        elif route == "/api/world/{worldId}/event" and method == RESTMethod.POST:
            self.location_use_case.create(world.id, name=anon_name(), span=span, profile=profile)
            self.traveler_use_case.create(world.id, name=anon_name(), journey=journey, profile=profile)
        elif route in {"/api/world/{worldId}/locations"} and method == RESTMethod.GET:
            self.location_use_case.create(world.id, name="The Great Pyramid", tags=tags, span=span, profile=profile)
        elif route == "/api/world/{worldId}/location/{locationId}" and method in {RESTMethod.GET, RESTMethod.PATCH, RESTMethod.DELETE}:
            location = self.location_use_case.create(
                world.id, name="The Great Pyramid", tags=tags, span=span, attributes=attributes, profile=profile,
                description="A great triangular structure in Egypt constructed long ago.")
            url_params["location_id"] = str(location.id)
        elif route in {"/api/world/{worldId}/travelers"} and method == RESTMethod.GET:
            self.traveler_use_case.create(world.id, name="Gaius Julius Caesar", tags=tags, journey=journey, profile=profile)
        elif (route == "/api/world/{worldId}/traveler/{travelerId}" and method in {RESTMethod.GET, RESTMethod.PATCH, RESTMethod.DELETE})\
                or (route == "/api/world/{worldId}/traveler/{travelerId}/journey" and method == RESTMethod.POST):
            traveler = self.traveler_use_case.create(
                world.id, name="Gaius Julius Caesar", tags=tags, journey=journey, attributes=attributes, profile=profile,
                description="Gaius Julius Caesar was a Roman general and statesman.")
            url_params["traveler_id"] = str(traveler.id)
        elif route in {"/api/world/{worldId}/events"} and method == RESTMethod.GET:
            self.event_use_case.create(world.id, name="Skirmish in the market", tags=tags, span=span, profile=profile)
        elif route == "/api/world/{worldId}/event/{eventId}" and method in {RESTMethod.GET, RESTMethod.PATCH, RESTMethod.DELETE}:
            traveler = self.traveler_use_case.create(
                world.id, name="Gaius Julius Caesar", tags=tags, journey=journey, attributes=attributes, profile=profile,
                description="Gaius Julius Caesar was a Roman general and statesman.")
            location = self.location_use_case.create(
                world.id, name="The Great Pyramid", tags=tags, span=span, attributes=attributes, profile=profile,
                description="A great triangular structure in Egypt constructed long ago.")
            event = self.event_use_case.create(
                world.id, name="Skirmish in the market", tags=tags, span=span, attributes=attributes, profile=profile,
                affected_locations=[location.id], affected_travelers=[traveler.id],
                description="Attacked by the Brigand Band, the civilians ran in despair until the courageous Band Of Defenders came to "
                            "the rescue.")
            url_params["event_id"] = str(event.id)
        elif route in "/api/world/{worldId}/location/{locationId}/timeline" and method == RESTMethod.GET:
            location = self.location_use_case.create(world.id, **anon_create_location_kwargs(span=span), profile=profile)
            self.event_use_case.create(world.id, **anon_create_event_kwargs(
                span=span, affected_locations={location.id}, tags=tags), profile=profile)
            url_params["location_id"] = str(location.id)
        elif route in "/api/world/{worldId}/traveler/{travelerId}/timeline" and method == RESTMethod.GET:
            traveler = self.traveler_use_case.create(world.id, **anon_create_traveler_kwargs(journey=journey), profile=profile)
            self.event_use_case.create(world.id, **anon_create_event_kwargs(
                span=span, affected_travelers={traveler.id}, tags=tags), profile=profile)
            url_params["traveler_id"] = str(traveler.id)

        return url_params if url_params else None

    @parameterized.expand(_get_test_params())
    @patch("application.use_case.event_use_cases.generate_prefixed_id")
    @patch("application.use_case.traveler_use_cases.generate_prefixed_id")
    @patch("application.use_case.location_use_cases.generate_prefixed_id")
    @patch("application.use_case.world_use_cases.generate_prefixed_id")
    def test__api_route__(
            self, _test_name,
            route: str, method: RESTMethod, world_id_generator_mock: MagicMock, location_id_generator_mock: MagicMock,
            traveler_id_generator_mock: MagicMock, event_id_generator_mock: MagicMock,
    ) -> None:
        # Arrange
        world_id_generator_mock.side_effect = _dummy_id_generator
        location_id_generator_mock.side_effect = _dummy_id_generator
        traveler_id_generator_mock.side_effect = _dummy_id_generator
        event_id_generator_mock.side_effect = _dummy_id_generator

        url_params = self._set_up_for(route, method)

        json_body = self.api_spec.get_resource_request_body_examples(route, method).get("application/json")
        query_params = self.api_spec.get_resource_request_query_param_examples(route, method)
        expected_response_bodies = self.api_spec.get_resource_response_body_examples(route, method)
        internal_route = _correct_url_params(route)

        # Act
        actual_status_code, actual_response_body = self.controller.invoke(
            internal_route, method, url_params=url_params, json=json_body, query_params=query_params)

        # Assert
        self.assertNotErrorResponse(actual_response_body)
        actual_status_code_str = str(actual_status_code.real)
        self.assertIn(actual_status_code_str, expected_response_bodies)
        expected_response_body = _extract_response_body(actual_status_code_str, "application/json", expected_response_bodies)
        self.assertEqual(expected_response_body, actual_response_body)

    def assertNotErrorResponse(self, response_body: str) -> None:
        if response_body.startswith('{"error":'):
            self.fail(loads(response_body)["error"])
