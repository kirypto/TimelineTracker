from abc import ABC, abstractmethod
from typing import Tuple, Dict, Union, List, Any


class LocationsRequestHandler(ABC):
    @abstractmethod
    def locations_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def locations_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        pass

    @abstractmethod
    def location_get_handler(self, location_id_str: str) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def location_delete_handler(self, location_id_str: str) -> Tuple[Union[dict, str], int]:
        pass

    @abstractmethod
    def location_patch_handler(self, location_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def location_timeline_get_handler(self, location_id_str: str, query_params: Dict[str, str]) -> Tuple[List[str], int]:
        pass


class TravelersRequestHandler:
    @abstractmethod
    def travelers_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def travelers_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        pass

    @abstractmethod
    def traveler_get_handler(self, traveler_id_str: str) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def traveler_delete_handler(self, traveler_id_str: str) -> Tuple[Union[dict, str], int]:
        pass

    @abstractmethod
    def traveler_patch_handler(self, traveler_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def traveler_journey_post_handler(self, traveler_id_str: str, new_positional_move_json: dict) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def traveler_timeline_get_handler(self, traveler_id_str: str, query_params: Dict[str, str]) -> Tuple[List[Union[str, dict]], int]:
        pass


class EventsRequestHandler:
    @abstractmethod
    def events_post_handler(self, request_body: dict) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def events_get_all_handler(self, query_params: Dict[str, str]) -> Tuple[Union[list, dict], int]:
        pass

    @abstractmethod
    def event_get_handler(self, event_id_str: str) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def event_delete_handler(self, event_id_str: str) -> Tuple[Union[dict, str], int]:
        pass

    @abstractmethod
    def event_patch_handler(self, event_id_str: str, patch_operations: List[Dict[str, Any]]) -> Tuple[dict, int]:
        pass