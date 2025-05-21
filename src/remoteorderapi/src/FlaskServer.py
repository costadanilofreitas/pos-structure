from flask import Flask, request, jsonify, Response
from typing import List
from threading import Thread
import requests
from orderservice import OrderService
from storeservice import StoreService
from chatservice import ChatService
from customexception import ValidationException
from InternalError import InternalError
from RemoteOrderJsonEncoder import RemoteOrderJsonEncoder
from functools import wraps
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask("FlaskRoutes")
app.json_encoder = RemoteOrderJsonEncoder

order_service = None  # type: OrderService
store_service = None  # type: StoreService
chat_service = None  # type: ChatService
# The dictionary of headers that are added to every response
server_allowed_urls = {}


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
        if self.app_thread is None or not self.app_thread.is_alive():
            return

        requests.request("POST", "http://localhost:{0}".format(self.port) + "/shutdown")


def set_allowed_urls(allowed_urls):
    # type: (List[unicode]) -> None
    for allowed_url in allowed_urls:
        server_allowed_urls[allowed_url] = allowed_url


def add_default_headers(f):
    @wraps(f)
    def decorated_function(*args, **kargs):
        response = f(*args, **kargs)  # type: Response

        if response is None:
            response = Response()

        if isinstance(response, str):
            response = Response(response)
            response.headers["Content-Type"] = "application/json"

        if isinstance(response, tuple):
            if isinstance(response[0], str):
                response = Response(response[0], response[1])
                response.headers["Content-Type"] = "application/json"
            elif isinstance(response[0], Response):
                original_tuple = response

                response = response[0]
                if len(original_tuple) > 1:
                    response.status = str(original_tuple[1])

        if "Origin" in request.headers:
            origin = request.headers["Origin"]
            if origin is not None and origin in server_allowed_urls:
                if "Access-Control-Allow-Origin" not in response.headers:
                    response.headers.add("Access-Control-Allow-Origin", origin)

        return response
    return decorated_function


@app.route('/orders/inProduction', methods=['GET'])
@add_default_headers
def get_tasks():
    try:
        order_in_queue_json = order_service.get_stored_orders()
        return order_in_queue_json
    except Exception as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/orders/sendToProduction/<order_id>', methods=['GET'])
@add_default_headers
def send_to_production(order_id):
    # type: (int) -> tuple
    try:
        order_service.send_order_to_production(order_id)
        return "", 200
    except ValidationException as er:
        return jsonify(er), 400
    except BaseException as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/orders/reprint/<order_id>/<retransmit_id>', methods=['GET'])
@add_default_headers
def reprint(order_id, retransmit_id):
    # type: (int) -> tuple
    try:
        order_service.reprint_delivery_order(order_id, retransmit_id)
        return "", 200
    except ValidationException as er:
        return jsonify(er), 400
    except BaseException as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/store', methods=['GET'])
@add_default_headers
def get_store_info():
    try:
        store = store_service.get_store()
        return store
    except BaseException as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/store/open', methods=['GET'])
@add_default_headers
def open_store():
    try:
        store = store_service.open_store()
        return store
    except ValidationException as ve:
        return jsonify(ve), 409
    except BaseException as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/store/close', methods=['GET'])
@add_default_headers
def close_store():
    try:
        store = store_service.close_store()
        return store
    except ValidationException as ve:
        return jsonify(ve), 409
    except BaseException as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/chat/sendMessage', methods=['POST'])
@add_default_headers
def send_message():
    try:
        message_data = request.get_data()
        chat_service.send_message(message_data)
    except ValidationException as ex:
        return jsonify(ex), 400
    except Exception as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/chat/updates/<message_id>', methods=['GET'])
@add_default_headers
def get_unread_messages(message_id):
    try:
        messages = chat_service.get_updates(str(message_id))
        return messages
    except Exception as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/chat/lastMessages', methods=['GET'])
@add_default_headers
def get_last_messages():
    try:
        quantity = request.args.get('quantity')
        if quantity is None:
            quantity_data = ""
        else:
            try:
                quantity_data = str(int(quantity))
            except:
                quantity_data = ""

        messages = chat_service.get_last_messages(quantity_data)
        return messages
    except Exception as ex:
        error_object = InternalError(repr(ex))
        return jsonify(error_object), 500


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
