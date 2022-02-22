from abc import ABC, abstractmethod
from typing import Callable

from application.requests.rest import RESTMethod, RequestHandler, MIMEType


HandlerRegisterer = Callable[[RequestHandler], None]


class RESTController(ABC):
    @abstractmethod
    def register_rest_endpoint(
            self, route: str, method: RESTMethod, response_type: MIMEType = MIMEType.JSON, *, json: bool = False, query_params: bool = False
    ) -> HandlerRegisterer:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass
