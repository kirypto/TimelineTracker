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


class WorldsRESTRequestHandler:
    @staticmethod
    def register_routes(rest_controller: RESTController, world_use_case: WorldUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/world", RESTMethod.POST, MIMEType.JSON, json=True)
        def world_post_handler(json_body: dict, **kwargs) -> HandlerResult:
            world_kwargs = {
                "name": JsonTranslator.from_json(json_body["name"], str),
                "description": JsonTranslator.from_json(json_body.get("description", ""), str),
                "metadata": JsonTranslator.from_json(json_body.get("metadata", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(json_body.get("tags", set()), Set[Tag]),
            }
            location = world_use_case.create(**world_kwargs, **kwargs)

            return HTTPStatus.CREATED, dumps(JsonTranslator.to_json(location), indent=2)


class LocationsRestRequestHandler:
    @staticmethod
    def register_routes(rest_controller: RESTController, location_use_case: LocationUseCase, timeline_use_case: TimelineUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/location", RESTMethod.POST, MIMEType.JSON, json=True)
        def locations_post_handler(json_body: dict, **kwargs) -> HandlerResult:
            location_kwargs = {
                "name": JsonTranslator.from_json(json_body["name"], str),
                "description": JsonTranslator.from_json(json_body.get("description", ""), str),
                "span": JsonTranslator.from_json(json_body["span"], PositionalRange),
                "metadata": JsonTranslator.from_json(json_body.get("metadata", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(json_body.get("tags", set()), Set[Tag]),
            }
            location = location_use_case.create(**location_kwargs, **kwargs)

            return HTTPStatus.CREATED, dumps(JsonTranslator.to_json(location), indent=2)

        @rest_controller.register_rest_endpoint("/api/locations", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def locations_get_all_handler(query_params: Dict[str, str], **kwargs) -> HandlerResult:
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

            locations = location_use_case.retrieve_all(**filters, **kwargs)

            return HTTPStatus.OK, dumps([JsonTranslator.to_json(location.id) for location in locations], indent=2)

        @rest_controller.register_rest_endpoint("/api/location/<location_id>", RESTMethod.GET, MIMEType.JSON)
        def location_get_handler(*, location_id: str, **kwargs) -> HandlerResult:
            if not location_id.startswith("location-"):
                raise ValueError(f"Cannot parse location id from '{location_id}")
            _location_id = JsonTranslator.from_json(location_id, PrefixedUUID)

            location = location_use_case.retrieve(_location_id, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(location), indent=2)

        @rest_controller.register_rest_endpoint("/api/location/<location_id>", RESTMethod.DELETE, MIMEType.JSON)
        def location_delete_handler(*, location_id: str, **kwargs) -> HandlerResult:
            if not location_id.startswith("location-"):
                raise ValueError(f"Cannot parse location id from '{location_id}")
            location_id_ = JsonTranslator.from_json(location_id, PrefixedUUID)

            location_use_case.delete(location_id_, **kwargs)

            return HTTPStatus.NO_CONTENT, ""

        @rest_controller.register_rest_endpoint("/api/location/<location_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def location_patch_handler(body_patch_operations: List[Dict[str, Any]], *, location_id: str, **kwargs) -> HandlerResult:
            if not location_id.startswith("location-"):
                raise ValueError(f"Cannot parse location id from '{location_id}")
            location_id_ = JsonTranslator.from_json(location_id, PrefixedUUID)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_location_json = JsonTranslator.to_json(location_use_case.retrieve(location_id_, **kwargs))

            modified_location_json = patch.apply(existing_location_json)
            modified_location = JsonTranslator.from_json(modified_location_json, Location)

            if modified_location.id != location_id_:
                raise ValueError("A Location's 'id' cannot be modified")

            location_use_case.update(modified_location, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(modified_location), indent=2)

        @rest_controller.register_rest_endpoint(
            "/api/location/<location_id>/timeline", RESTMethod.GET, MIMEType.JSON, query_params=True
        )
        def location_timeline_get_handler(query_params: Dict[str, str], *, location_id: str, **kwargs) -> HandlerResult:
            if not location_id.startswith("location-"):
                raise ValueError(f"Cannot parse location id from '{location_id}")
            location_id_ = JsonTranslator.from_json(location_id, PrefixedUUID)

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

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(timeline), indent=2)


class TravelersRestRequestHandler:
    @staticmethod
    def register_routes(rest_controller: RESTController, traveler_use_case: TravelerUseCase, timeline_use_case: TimelineUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/traveler", RESTMethod.POST, MIMEType.JSON, json=True)
        def travelers_post_handler(request_body: dict, **kwargs) -> HandlerResult:
            traveler_kwargs = {
                "name": JsonTranslator.from_json(request_body["name"], str),
                "description": JsonTranslator.from_json(request_body.get("description", ""), str),
                "journey": JsonTranslator.from_json(request_body["journey"], List[PositionalMove]),
                "metadata": JsonTranslator.from_json(request_body.get("metadata", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(request_body.get("tags", set()), Set[Tag]),
            }
            traveler = traveler_use_case.create(**traveler_kwargs, **kwargs)

            return HTTPStatus.CREATED, dumps(JsonTranslator.to_json(traveler), indent=2)

        @rest_controller.register_rest_endpoint("/api/travelers", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def travelers_get_all_handler(query_params: Dict[str, str], **kwargs) -> HandlerResult:
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

            travelers = traveler_use_case.retrieve_all(**filters, **kwargs)

            return HTTPStatus.OK, dumps([JsonTranslator.to_json(traveler.id) for traveler in travelers], indent=2)

        @rest_controller.register_rest_endpoint("/api/traveler/<traveler_id>", RESTMethod.GET, MIMEType.JSON)
        def traveler_get_handler(*, traveler_id: str, **kwargs) -> HandlerResult:
            if not traveler_id.startswith("traveler-"):
                raise ValueError(f"Cannot parse traveler id from '{traveler_id}")
            traveler_id_ = JsonTranslator.from_json(traveler_id, PrefixedUUID)

            traveler = traveler_use_case.retrieve(traveler_id_, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(traveler), indent=2)

        @rest_controller.register_rest_endpoint("/api/traveler/<traveler_id>", RESTMethod.DELETE, MIMEType.JSON)
        def traveler_delete_handler(*, traveler_id: str, **kwargs) -> HandlerResult:
            if not traveler_id.startswith("traveler-"):
                raise ValueError(f"Cannot parse traveler id from '{traveler_id}")
            traveler_id = JsonTranslator.from_json(traveler_id, PrefixedUUID)

            traveler_use_case.delete(traveler_id, **kwargs)

            return HTTPStatus.NO_CONTENT, dumps("", indent=2)

        @rest_controller.register_rest_endpoint("/api/traveler/<traveler_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def traveler_patch_handler(body_patch_operations: List[Dict[str, Any]], *, traveler_id: str, **kwargs) -> HandlerResult:
            if not traveler_id.startswith("traveler-"):
                raise ValueError(f"Cannot parse traveler id from '{traveler_id}")
            traveler_id_ = JsonTranslator.from_json(traveler_id, PrefixedUUID)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_object_view = JsonTranslator.to_json(traveler_use_case.retrieve(traveler_id_, **kwargs))

            modified_traveler_json = patch.apply(existing_object_view)
            modified_traveler = JsonTranslator.from_json(modified_traveler_json, Traveler)

            if modified_traveler.id != traveler_id_:
                raise ValueError("A Traveler's 'id' cannot be modified")

            traveler_use_case.update(modified_traveler, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(modified_traveler), indent=2)

        @rest_controller.register_rest_endpoint("/api/traveler/<traveler_id>/journey", RESTMethod.POST, MIMEType.JSON, json=True)
        def traveler_journey_post_handler(body_new_positional_move: dict, *, traveler_id: str, **kwargs) -> HandlerResult:
            if not traveler_id.startswith("traveler-"):
                raise ValueError(f"Cannot parse traveler id from '{traveler_id}")
            traveler_id_ = JsonTranslator.from_json(traveler_id, PrefixedUUID)

            new_positional_move = JsonTranslator.from_json(body_new_positional_move, PositionalMove)

            existing_traveler = traveler_use_case.retrieve(traveler_id_, **kwargs)

            appended_journey = deepcopy(existing_traveler.journey)
            appended_journey.append(new_positional_move)
            modified_traveler = Traveler(
                id=existing_traveler.id, name=existing_traveler.name, description=existing_traveler.description,
                journey=appended_journey, tags=existing_traveler.tags, metadata=existing_traveler.metadata)

            traveler_use_case.update(modified_traveler, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(modified_traveler), indent=2)

        @rest_controller.register_rest_endpoint(
            "/api/traveler/<traveler_id>/timeline", RESTMethod.GET, MIMEType.JSON, query_params=True
        )
        def traveler_timeline_get_handler(query_params: Dict[str, str], *, traveler_id: str, **kwargs) -> HandlerResult:
            if not traveler_id.startswith("traveler-"):
                raise ValueError(f"Cannot parse traveler id from '{traveler_id}")
            traveler_id = JsonTranslator.from_json(traveler_id, PrefixedUUID)

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

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(timeline), indent=2)


class EventsRestRequestHandler:
    _event_use_case: EventUseCase
    _rest_controller: RESTController

    @staticmethod
    def register_routes(rest_controller: RESTController, event_use_case: EventUseCase) -> None:
        @rest_controller.register_rest_endpoint("/api/event", RESTMethod.POST, MIMEType.JSON, json=True)
        def events_post_handler(request_body: dict, **kwargs) -> HandlerResult:
            event_kwargs = {
                "name": JsonTranslator.from_json(request_body["name"], str),
                "description": JsonTranslator.from_json(request_body.get("description", ""), str),
                "span": JsonTranslator.from_json(request_body["span"], PositionalRange),
                "metadata": JsonTranslator.from_json(request_body.get("metadata", {}), Dict[str, str]),
                "tags": JsonTranslator.from_json(request_body.get("tags", set()), Set[Tag]),
                "affected_locations": JsonTranslator.from_json(request_body["affected_locations"], Set[PrefixedUUID]),
                "affected_travelers": JsonTranslator.from_json(request_body["affected_travelers"], Set[PrefixedUUID]),
            }
            event = event_use_case.create(**event_kwargs, **kwargs)

            return HTTPStatus.CREATED, dumps(JsonTranslator.to_json(event), indent=2)

        @rest_controller.register_rest_endpoint("/api/events", RESTMethod.GET, MIMEType.JSON, query_params=True)
        def events_get_all_handler(query_params: Dict[str, str], **kwargs) -> HandlerResult:
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

            events = event_use_case.retrieve_all(**filters, **kwargs)

            return HTTPStatus.OK, dumps([JsonTranslator.to_json(event.id) for event in events], indent=2)

        @rest_controller.register_rest_endpoint("/api/event/<event_id>", RESTMethod.GET, MIMEType.JSON)
        def event_get_handler(*, event_id: str, **kwargs) -> HandlerResult:
            if not event_id.startswith("event-"):
                raise ValueError(f"Cannot parse event id from '{event_id}")
            event_id_ = JsonTranslator.from_json(event_id, PrefixedUUID)

            event = event_use_case.retrieve(event_id_, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(event), indent=2)

        @rest_controller.register_rest_endpoint("/api/event/<event_id>", RESTMethod.DELETE, MIMEType.JSON)
        def event_delete_handler(*, event_id: str, **kwargs) -> HandlerResult:
            if not event_id.startswith("event-"):
                raise ValueError(f"Cannot parse event id from '{event_id}")
            event_id_ = JsonTranslator.from_json(event_id, PrefixedUUID)

            event_use_case.delete(event_id_, **kwargs)

            return HTTPStatus.NO_CONTENT, dumps("", indent=2)

        @rest_controller.register_rest_endpoint("/api/event/<event_id>", RESTMethod.PATCH, MIMEType.JSON, json=True)
        def event_patch_handler(body_patch_operations: List[Dict[str, Any]], *, event_id: str, **kwargs) -> HandlerResult:
            if not event_id.startswith("event-"):
                raise ValueError(f"Cannot parse event id from '{event_id}")
            event_id_ = JsonTranslator.from_json(event_id, PrefixedUUID)

            patch = JsonPatch([PatchOperation(operation).operation for operation in body_patch_operations])
            existing_event_json = JsonTranslator.to_json(event_use_case.retrieve(event_id_, **kwargs))

            modified_event_json = patch.apply(existing_event_json)
            modified_event = JsonTranslator.from_json(modified_event_json, Event)

            if modified_event.id != event_id_:
                raise ValueError("A Event's 'id' cannot be modified")

            event_use_case.update(modified_event, **kwargs)

            return HTTPStatus.OK, dumps(JsonTranslator.to_json(modified_event), indent=2)
