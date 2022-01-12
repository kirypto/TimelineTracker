from abc import ABC, abstractmethod
from typing import Set

from application.requests.rest import RouteDescriptor


class AbstractRESTHandler(ABC):
    @abstractmethod
    def get_routes(self) -> Set[RouteDescriptor]:
        pass
