from typing import Dict

from simplehttprouter import HttpRouter, Route
from messageprocessor import ApiRouter
from messageprocessor import MessageProcessor


class DefaultApiRouter(ApiRouter):
    def __init__(self, router, processors):
        # type: (HttpRouter, Dict[Route, MessageProcessor]) -> None
        self.router = router
        self.processors = processors

    def get_message_processor(self, api_request):
        route = self.router.get_route(Route(api_request.method, api_request.api_path))
        if route not in self.processors:
            return None
        return self.processors[route]
