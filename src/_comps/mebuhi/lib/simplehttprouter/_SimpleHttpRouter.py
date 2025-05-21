import re
from typing import List

from ._Route import Route
from ._HttpRouter import HttpRouter


class SimpleHttpRouter(HttpRouter):
    def __init__(self, routes):
        # type: (List[Route]) -> None
        self.routes = []
        for route in routes:
            self.routes.append(
                InternalRoute(route, "^" + route.method + "#" + re.sub("{.*?}", "(.*)", route.path + "$")))

    def get_route(self, route):
        for internal_route in self.routes:
            if re.search(internal_route.url_regex, route.method + "#" + route.path) is not None:
                return internal_route.original_route
        return None

    def get_path_parameters(self, route):
        for internal_route in self.routes:
            match = re.match(internal_route.url_regex, route.method + "#" + route.path)
            if match:
                path_parameters = {}
                parameters = re.match(
                    internal_route.url_regex,
                    internal_route.original_route.method + "#" + internal_route.original_route.path)
                for i in range(0, len(match.groups())):
                    parameter_name = parameters.groups()[i][1:-1]
                    parameter_value = match.groups()[i]
                    path_parameters[parameter_name] = parameter_value
                return path_parameters
        return None



class InternalRoute(object):
    def __init__(self, route, url_regex):
        self.original_route = route
        self.url_regex = url_regex
