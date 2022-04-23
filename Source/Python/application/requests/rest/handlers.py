from copy import deepcopy
from http import HTTPStatus
from json import dumps
from typing import Set, Dict, List, Any

from jsonpatch import JsonPatch, PatchOperation

from application.requests.data_forms import JsonTranslator
from application.requests.rest import RESTMethod, HandlerResult, MIMEType
from application.requests.rest.controllers import RESTController
from application.requests.rest.utils import parse_optional_tag_set_query_param, parse_optional_position_query_param, \
    parse_optional_positional_range_query_param
from application.use_case.event_use_cases import EventUseCase
from application.use_case.location_use_cases import LocationUseCase
from application.use_case.timeline_use_cases import TimelineUseCase
from application.use_case.traveler_use_cases import TravelerUseCase
from application.use_case.world_use_cases import WorldUseCase
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.positions import PositionalRange, PositionalMove
from domain.tags import Tag
from domain.travelers import Traveler
from domain.worlds import World, to_world_id


def _parse_world_id(world_id_raw: str) -> PrefixedUUID:
    if not world_id_raw.startswith("world-"):
        raise ValueError(f"Cannot parse world id from '{world_id_raw}")
    return JsonTranslator.from_json(world_id_raw, PrefixedUUID)


def _parse_location_id(location_id_raw: str) -> PrefixedUUID:
    if not location_id_raw.startswith("location-"):
        raise ValueError(f"Cannot parse location id from '{location_id_raw}")
    return JsonTranslator.from_json(location_id_raw, PrefixedUUID)


def _parse_traveler_id(traveler_id_raw: str) -> PrefixedUUID:
    if not traveler_id_raw.startswith("traveler-"):
        raise ValueError(f"Cannot parse traveler id from '{traveler_id_raw}")
    return JsonTranslator.from_json(traveler_id_raw, PrefixedUUID)


def _parse_event_id(event_id_raw: str) -> PrefixedUUID:
    if not event_id_raw.startswith("event-"):
        raise ValueError(f"Cannot parse event id from '{event_id_raw}")
    return JsonTranslator.from_json(event_id_raw, PrefixedUUID)


class WorldsRESTRequestHandler:
    @staticmethod
    def register_routes(rest_controller: RESTController, world_use_case: WorldUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/world", RESTMethod.POST, MIMEType.JSON, json=True)
        def world_post_handler(json_body: dict, **kwargs) -> HandlerResult:
            world_kwargs = {
                "name": JsonTranslator.from_json(json_body["name"], str),
                "description": JsonTranslator.from_json(json_body.get("description", ""), str),
                "attributes": JsonTranslator.from_json(json_body.get("attributes", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(json_body.get("tags", set()), Set[Tag]),
            }
            world = world_use_case.create(**world_kwargs, **kwargs)

            return HTTPStatus.CREATED, JsonTranslator.to_json_str(world)

        @rest_controller.register_rest_endpoint("/api/worlds", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def worlds_get_handler(query_params: Dict[str, str], **kwargs) -> HandlerResult:
            supported_filters = {"nameIs", "nameHas", "taggedAll", "taggedAny", "taggedOnly", "taggedNone"}
            if not supported_filters.issuperset(query_params.keys()):
                raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
            filters = {
                "name_is": query_params.get("nameIs", None),
                "name_has": query_params.get("nameHas", None),
                "tagged_all": parse_optional_tag_set_query_param(query_params.get("taggedAll", None)),
                "tagged_any": parse_optional_tag_set_query_param(query_params.get("taggedAny", None)),
                "tagged_only": parse_optional_tag_set_query_param(query_params.get("taggedOnly", None)),
                "tagged_none": parse_optional_tag_set_query_param(query_params.get("taggedNone", None)),
            }

            world_ids = [world.id for world in world_use_case.retrieve_all(**filters, **kwargs)]

            return HTTPStatus.OK, JsonTranslator.to_json_str(world_ids)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>", RESTMethod.GET, MIMEType.JSON)
        def world_get_handler(*, world_id: str, **kwargs) -> HandlerResult:
            world_id_ = _parse_world_id(world_id)

            world = world_use_case.retrieve(world_id_, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(world)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def world_patch_handler(body_patch_operations: List[Dict[str, Any]], *, world_id: str, **kwargs) -> HandlerResult:
            world_id_ = _parse_world_id(world_id)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_world_json = JsonTranslator.to_json(world_use_case.retrieve(world_id_, **kwargs))

            modified_world_json = patch.apply(existing_world_json)
            modified_world = JsonTranslator.from_json(modified_world_json, World)

            if modified_world.id != world_id_:
                raise ValueError("A World's 'id' cannot be modified")

            world_use_case.update(modified_world, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(modified_world)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>", RESTMethod.DELETE, MIMEType.JSON)
        def world_delete_handler(*, world_id: str, **kwargs) -> HandlerResult:
            world_id_ = _parse_world_id(world_id)

            world_use_case.delete(world_id_, **kwargs)

            return HTTPStatus.NO_CONTENT, ""


class LocationsRestRequestHandler:
    @staticmethod
    def register_routes(rest_controller: RESTController, location_use_case: LocationUseCase, timeline_use_case: TimelineUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/world/<world_id>/location", RESTMethod.POST, MIMEType.JSON, json=True)
        def locations_post_handler(json_body: dict, *, world_id: str, **kwargs) -> HandlerResult:
            location_kwargs = {
                "name": JsonTranslator.from_json(json_body["name"], str),
                "description": JsonTranslator.from_json(json_body.get("description", ""), str),
                "span": JsonTranslator.from_json(json_body["span"], PositionalRange),
                "attributes": JsonTranslator.from_json(json_body.get("attributes", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(json_body.get("tags", set()), Set[Tag]),
            }
            location = location_use_case.create(to_world_id(world_id), **location_kwargs, **kwargs)

            return HTTPStatus.CREATED, JsonTranslator.to_json_str(location)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/locations", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def locations_get_all_handler(query_params: Dict[str, str], *, world_id: str, **kwargs) -> HandlerResult:
            supported_filters = {
                "nameIs", "nameHas", "taggedAll", "taggedAny", "taggedOnly", "taggedNone", "spanIncludes", "spanIntersects"
            }
            if not supported_filters.issuperset(query_params.keys()):
                raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
            filters = {
                "name_is": query_params.get("nameIs", None),
                "name_has": query_params.get("nameHas", None),
                "tagged_all": parse_optional_tag_set_query_param(query_params.get("taggedAll", None)),
                "tagged_any": parse_optional_tag_set_query_param(query_params.get("taggedAny", None)),
                "tagged_only": parse_optional_tag_set_query_param(query_params.get("taggedOnly", None)),
                "tagged_none": parse_optional_tag_set_query_param(query_params.get("taggedNone", None)),
                "span_includes": parse_optional_position_query_param(query_params.get("spanIncludes", None)),
                "span_intersects": parse_optional_positional_range_query_param(query_params.get("spanIntersects", None)),
            }

            location_ids = [location.id for location in location_use_case.retrieve_all(**filters, **kwargs)]

            return HTTPStatus.OK, JsonTranslator.to_json_str(location_ids)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/location/<location_id>", RESTMethod.GET, MIMEType.JSON)
        def location_get_handler(*, world_id: str, location_id: str, **kwargs) -> HandlerResult:
            _location_id = _parse_location_id(location_id)

            location = location_use_case.retrieve(_location_id, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(location)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/location/<location_id>", RESTMethod.DELETE, MIMEType.JSON)
        def location_delete_handler(*, world_id: str, location_id: str, **kwargs) -> HandlerResult:
            location_id_ = _parse_location_id(location_id)

            location_use_case.delete(location_id_, **kwargs)

            return HTTPStatus.NO_CONTENT, ""

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/location/<location_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def location_patch_handler(body_patch_operations: List[Dict[str, Any]], *, world_id: str, location_id: str, **kwargs) -> HandlerResult:
            location_id_ = _parse_location_id(location_id)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_location_json = JsonTranslator.to_json(location_use_case.retrieve(location_id_, **kwargs))

            modified_location_json = patch.apply(existing_location_json)
            modified_location = JsonTranslator.from_json(modified_location_json, Location)

            if modified_location.id != location_id_:
                raise ValueError("A Location's 'id' cannot be modified")

            location_use_case.update(modified_location, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(modified_location)

        @rest_controller.register_rest_endpoint(
            "/api/world/<world_id>/location/<location_id>/timeline", RESTMethod.GET, MIMEType.JSON, query_params=True
        )
        def location_timeline_get_handler(query_params: Dict[str, str], *, world_id: str, location_id: str, **kwargs) -> HandlerResult:
            location_id_ = _parse_location_id(location_id)

            supported_filters = {"taggedAll", "taggedAny", "taggedOnly", "taggedNone"}
            if not supported_filters.issuperset(query_params.keys()):
                raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
            filters = {
                "tagged_all": parse_optional_tag_set_query_param(query_params.get("taggedAll", None)),
                "tagged_any": parse_optional_tag_set_query_param(query_params.get("taggedAny", None)),
                "tagged_only": parse_optional_tag_set_query_param(query_params.get("taggedOnly", None)),
                "tagged_none": parse_optional_tag_set_query_param(query_params.get("taggedNone", None)),
            }

            timeline = timeline_use_case.construct_location_timeline(location_id_, **filters, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(timeline)


class TravelersRestRequestHandler:
    @staticmethod
    def register_routes(rest_controller: RESTController, traveler_use_case: TravelerUseCase, timeline_use_case: TimelineUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/world/<world_id>/traveler", RESTMethod.POST, MIMEType.JSON, json=True)
        def travelers_post_handler(request_body: dict, *, world_id: str, **kwargs) -> HandlerResult:
            traveler_kwargs = {
                "name": JsonTranslator.from_json(request_body["name"], str),
                "description": JsonTranslator.from_json(request_body.get("description", ""), str),
                "journey": JsonTranslator.from_json(request_body["journey"], List[PositionalMove]),
                "attributes": JsonTranslator.from_json(request_body.get("attributes", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(request_body.get("tags", set()), Set[Tag]),
            }
            traveler = traveler_use_case.create(to_world_id(world_id), **traveler_kwargs, **kwargs)

            return HTTPStatus.CREATED, JsonTranslator.to_json_str(traveler)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/travelers", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def travelers_get_all_handler(query_params: Dict[str, str], *, world_id: str, **kwargs) -> HandlerResult:
            supported_filters = {"nameIs", "nameHas", "taggedAll", "taggedAny", "taggedOnly", "taggedNone", "journeyIntersects",
                                 "journeyIncludes"}
            if not supported_filters.issuperset(query_params.keys()):
                raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
            filters = {
                "name_is": query_params.get("nameIs", None),
                "name_has": query_params.get("nameHas", None),
                "tagged_all": parse_optional_tag_set_query_param(query_params.get("taggedAll", None)),
                "tagged_any": parse_optional_tag_set_query_param(query_params.get("taggedAny", None)),
                "tagged_only": parse_optional_tag_set_query_param(query_params.get("taggedOnly", None)),
                "tagged_none": parse_optional_tag_set_query_param(query_params.get("taggedNone", None)),
                "journey_intersects": parse_optional_positional_range_query_param(query_params.get("journeyIntersects", None)),
                "journey_includes": parse_optional_position_query_param(query_params.get("journeyIncludes", None)),
            }

            traveler_ids = [traveler.id for traveler in traveler_use_case.retrieve_all(**filters, **kwargs)]

            return HTTPStatus.OK, JsonTranslator.to_json_str(traveler_ids)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/traveler/<traveler_id>", RESTMethod.GET, MIMEType.JSON)
        def traveler_get_handler(*, world_id: str, traveler_id: str, **kwargs) -> HandlerResult:
            traveler_id_ = _parse_traveler_id(traveler_id)

            traveler = traveler_use_case.retrieve(traveler_id_, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(traveler)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/traveler/<traveler_id>", RESTMethod.DELETE, MIMEType.JSON)
        def traveler_delete_handler(*, world_id: str, traveler_id: str, **kwargs) -> HandlerResult:
            traveler_id = _parse_traveler_id(traveler_id)

            traveler_use_case.delete(traveler_id, **kwargs)

            return HTTPStatus.NO_CONTENT, dumps("", indent=2)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/traveler/<traveler_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def traveler_patch_handler(body_patch_operations: List[Dict[str, Any]], *, world_id: str, traveler_id: str, **kwargs) -> HandlerResult:
            traveler_id_ = _parse_traveler_id(traveler_id)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_object_view = JsonTranslator.to_json(traveler_use_case.retrieve(traveler_id_, **kwargs))

            modified_traveler_json = patch.apply(existing_object_view)
            modified_traveler = JsonTranslator.from_json(modified_traveler_json, Traveler)

            if modified_traveler.id != traveler_id_:
                raise ValueError("A Traveler's 'id' cannot be modified")

            traveler_use_case.update(modified_traveler, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(modified_traveler)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/traveler/<traveler_id>/journey", RESTMethod.POST, MIMEType.JSON, json=True)
        def traveler_journey_post_handler(body_new_positional_move: dict, *, world_id: str, traveler_id: str, **kwargs) -> HandlerResult:
            traveler_id_ = _parse_traveler_id(traveler_id)

            new_positional_move = JsonTranslator.from_json(body_new_positional_move, PositionalMove)

            existing_traveler = traveler_use_case.retrieve(traveler_id_, **kwargs)

            appended_journey = deepcopy(existing_traveler.journey)
            appended_journey.append(new_positional_move)
            modified_traveler = Traveler(
                id=existing_traveler.id, name=existing_traveler.name, description=existing_traveler.description,
                journey=appended_journey, tags=existing_traveler.tags, attributes=existing_traveler.attributes)

            traveler_use_case.update(modified_traveler, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(modified_traveler)

        @rest_controller.register_rest_endpoint(
            "/api/world/<world_id>/traveler/<traveler_id>/timeline", RESTMethod.GET, MIMEType.JSON, query_params=True
        )
        def traveler_timeline_get_handler(query_params: Dict[str, str], *, world_id: str, traveler_id: str, **kwargs) -> HandlerResult:
            traveler_id = _parse_traveler_id(traveler_id)

            supported_filters = {"taggedAll", "taggedAny", "taggedOnly", "taggedNone"}
            if not supported_filters.issuperset(query_params.keys()):
                raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
            filters = {
                "tagged_all": parse_optional_tag_set_query_param(query_params.get("taggedAll", None)),
                "tagged_any": parse_optional_tag_set_query_param(query_params.get("taggedAny", None)),
                "tagged_only": parse_optional_tag_set_query_param(query_params.get("taggedOnly", None)),
                "tagged_none": parse_optional_tag_set_query_param(query_params.get("taggedNone", None)),
            }

            timeline = timeline_use_case.construct_traveler_timeline(traveler_id, **filters, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(timeline)


class EventsRestRequestHandler:
    _event_use_case: EventUseCase
    _rest_controller: RESTController

    @staticmethod
    def register_routes(rest_controller: RESTController, event_use_case: EventUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/world/<world_id>/event", RESTMethod.POST, MIMEType.JSON, json=True)
        def events_post_handler(request_body: dict, *, world_id: str, **kwargs) -> HandlerResult:
            event_kwargs = {
                "name": JsonTranslator.from_json(request_body["name"], str),
                "description": JsonTranslator.from_json(request_body.get("description", ""), str),
                "span": JsonTranslator.from_json(request_body["span"], PositionalRange),
                "attributes": JsonTranslator.from_json(request_body.get("attributes", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(request_body.get("tags", set()), Set[Tag]),
                "affected_locations": JsonTranslator.from_json(request_body["affected_locations"], Set[PrefixedUUID]),
                "affected_travelers": JsonTranslator.from_json(request_body["affected_travelers"], Set[PrefixedUUID]),
            }
            event = event_use_case.create(to_world_id(world_id), **event_kwargs, **kwargs)

            return HTTPStatus.CREATED, JsonTranslator.to_json_str(event)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/events", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def events_get_all_handler(query_params: Dict[str, str], *, world_id: str, **kwargs) -> HandlerResult:
            supported_filters = {
                "nameIs", "nameHas", "taggedAll", "taggedAny", "taggedOnly", "taggedNone", "spanIncludes", "spanIntersects"
            }
            if not supported_filters.issuperset(query_params.keys()):
                raise ValueError(f"Unsupported filter(s): {', '.join(query_params.keys() - supported_filters)}")
            filters = {
                "name_is": query_params.get("nameIs", None),
                "name_has": query_params.get("nameHas", None),
                "tagged_all": parse_optional_tag_set_query_param(query_params.get("taggedAll", None)),
                "tagged_any": parse_optional_tag_set_query_param(query_params.get("taggedAny", None)),
                "tagged_only": parse_optional_tag_set_query_param(query_params.get("taggedOnly", None)),
                "tagged_none": parse_optional_tag_set_query_param(query_params.get("taggedNone", None)),
                "span_includes": parse_optional_position_query_param(query_params.get("spanIncludes", None)),
                "span_intersects": parse_optional_positional_range_query_param(query_params.get("spanIntersects", None)),
            }

            event_ids = [event.id for event in event_use_case.retrieve_all(**filters, **kwargs)]

            return HTTPStatus.OK, JsonTranslator.to_json_str(event_ids)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/event/<event_id>", RESTMethod.GET, MIMEType.JSON)
        def event_get_handler(*, world_id: str, event_id: str, **kwargs) -> HandlerResult:
            event_id_ = _parse_event_id(event_id)

            event = event_use_case.retrieve(event_id_, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(event)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/event/<event_id>", RESTMethod.DELETE, MIMEType.JSON)
        def event_delete_handler(*, world_id: str, event_id: str, **kwargs) -> HandlerResult:
            event_id_ = _parse_event_id(event_id)

            event_use_case.delete(event_id_, **kwargs)

            return HTTPStatus.NO_CONTENT, dumps("", indent=2)

        @rest_controller.register_rest_endpoint("/api/world/<world_id>/event/<event_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def event_patch_handler(body_patch_operations: List[Dict[str, Any]], *, world_id: str, event_id: str, **kwargs) -> HandlerResult:
            event_id_ = _parse_event_id(event_id)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_event_json = JsonTranslator.to_json(event_use_case.retrieve(event_id_, **kwargs))

            modified_event_json = patch.apply(existing_event_json)
            modified_event = JsonTranslator.from_json(modified_event_json, Event)

            if modified_event.id != event_id_:
                raise ValueError("A Event's 'id' cannot be modified")

            event_use_case.update(modified_event, **kwargs)

            return HTTPStatus.OK, JsonTranslator.to_json_str(modified_event)
