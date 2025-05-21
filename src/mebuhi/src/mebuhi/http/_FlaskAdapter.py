from logging import Logger
from werkzeug.serving import make_server
from threading import Thread

from flask import Flask, Request, Response, request
from simplehttprouter import SimpleHttpRouter, Route
from typing import Dict, Callable, Optional, Any


class FlaskAdapter(object):
    def __init__(self, routes, logger=None):
        # type: (Dict[Route, Callable[[Request], Response]], Optional[Logger]) -> None
        self.routes = routes
        self.logger = logger

        self.app = None
        self.router = SimpleHttpRouter(list(routes.keys()))
        self.server_thread = None
        self.srv = None
        self.ctx = None

    def start(self, name, host, port):
        # type: (str, str, int) -> Any
        self.app = Flask(name)
        self.app.add_url_rule("/", "catch_all",
                              self.handle_messages,
                              defaults={"path": "/"},
                              methods=["GET", "POST", "PUT", "OPTIONS", "HEAD", "DELETE"])
        self.app.add_url_rule("/<path:path>",
                              "catch_all",
                              self.handle_messages,
                              methods=["GET", "POST", "PUT", "OPTIONS", "HEAD", "DELETE"])
        if host is not None:
            self.server_thread = Thread(target=self.run_server, args=[host, port])
            self.server_thread.daemon = True
            self.server_thread.start()

        return self.app

    def stop(self):
        self.srv.shutdown()

    def run_server(self, host, port):
        self.srv = make_server(host, port, self.app, True)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.srv.serve_forever()

    def handle_messages(self, path):
        # type: (str) -> Response
        try:
            path = "/" + path if path != "/" else path
            method = request.method

            route = Route(method, path)
            found_route = self.router.get_route(route)
            path_parameters = self.router.get_path_parameters(route)
            if found_route is None:
                if self.logger:
                    self.logger.exception("No route found - Returning 404")
                return Response(status=404)

            func = self.routes[found_route]
            return func(path_parameters, request)
        except Exception as _:
            if self.logger:
                self.logger.exception("Unhandled request - Returning 404")
            return Response(status=500)
