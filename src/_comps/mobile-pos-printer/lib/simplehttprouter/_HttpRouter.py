from abc import ABCMeta, abstractmethod
from typing import Optional, Dict

from ._Route import Route


class HttpRouter(object):
    __meta__ = ABCMeta

    @abstractmethod
    def get_route(self, route):
        # type: (Route) -> Optional[Route]
        raise NotImplementedError()

    @abstractmethod
    def get_path_parameters(self, route):
        # type: (Route) -> Dict[str, str]
        raise NotImplementedError()
