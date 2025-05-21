#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests

from typing import List
from flask import Flask, request, jsonify, Response
from threading import Thread

from sysactions import AuthenticationFailed

app = Flask("FlaskRoutes")
# The dictionary of headers that are added to every response
server_allowed_urls = {}
sales_report_interactor = None

logger = logging.getLogger("ReportsApi")


class FlaskServer(object):
    def __init__(self, port):
        # type: (int) -> None
        self.port = port
        self.app_thread = None  # type: Thread

    def start(self):
        self.app_thread = Thread(target=app.run, kwargs={"port": self.port, "host": "0.0.0.0", "threaded": True})
        self.app_thread.daemon = True
        self.app_thread.start()

    def stop(self):
        if self.app_thread is None:
            return

        requests.request("POST", "http://localhost:{0}".format(self.port) + "/shutdown", timeout=20)


def set_allowed_urls(allowed_urls):
    # type: (List[unicode]) -> None
    for allowed_url in allowed_urls:
        server_allowed_urls[allowed_url] = allowed_url


@app.route('/reports/sales/<date>', methods=['OPTIONS', 'GET'])
def login(date):
    try:
        report = sales_report_interactor.dayle_sales_report(date)
        report['ip'] = request.host.split(':')[0]
        if report is None or report == "":
            return jsonify("report can't be generated"), 400

        return jsonify(report), 200
    except AuthenticationFailed:
        return "", 401
    except Exception as ex:
        return jsonify(ex), 500


@app.route('/reports/orders/<date>', methods=['OPTIONS', 'GET'])
def report_orders_by_date(date):
    try:
        report = sales_report_interactor.dayle_sales_orders(date)
        # report['ip'] = request.host.split(':')[0]
        if report is None or report == "":
            return jsonify("report can't be generated"), 400

        return jsonify(report), 200
    except AuthenticationFailed:
        return "", 401
    except Exception as ex:
        return jsonify(ex), 500



@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
