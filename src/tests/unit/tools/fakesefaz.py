# -*- coding: utf-8 -*-
import http.server
import threading
import pkg_resources
from abc import ABCMeta, abstractmethod
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RequestListener(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def request_received(self, path, body):
        # type: (str) -> None
        pass


class ReceivedRequest(object):
    def __init__(self, path, body):
        self.path = path
        self.body = body


class FakeSefazServer(RequestListener):
    def __init__(self, port, request_handler_class):
        self.port = port
        self.handler = request_handler_class
        self.httpd = None
        self.received_requests = []

        if issubclass(self.handler, NotifyListenersSefazHandler):
            self.handler.add_notify_listeners(self)

    def startServing(self):
        self.httpd = http.server.HTTPServer(("", self.port), self.handler)  # type: http.server.HttpServer
        threading.Thread(name='Sefaz Fake Server Thread', target=self.httpd.serve_forever).start()

    def stopServing(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def request_received(self, path, body):
        self.received_requests.append(ReceivedRequest(path, body))

    def has_received_request(self, path):
        for received_request in self.received_requests:  # type: ReceivedRequest
            if path == received_request.path:
                return True

        return False

    def received_request_body_contains(self, path, value):
        request_index = self._get_request_index(path)
        if request_index < 0:
            return False
        else:
            return value in self.received_requests[request_index].body

    def received_requests_are_valid_xmls(self):
        if len(self.received_requests) == 0:
            return False

        chrome = webdriver.Chrome()

        for received_request in self.received_requests:  # type: ReceivedRequest
            no_envelope = self._remove_envelope(received_request.body)

            chrome.get("https://www.sefaz.rs.gov.br/nfe/nfe-val.aspx")

            txtxml = chrome.find_element_by_id("txtxml")
            txtxml.send_keys(no_envelope)

            btnvalidar = chrome.find_element_by_id("btnvalidar")
            btnvalidar.click()

            WebDriverWait(chrome, 120).until(EC.presence_of_element_located((By.ID, "resultado")))

            try:
                error_image = chrome.find_element_by_css_selector("img[src='../Imagens/erro.png']")

                chrome.close()

                return False
            except NoSuchElementException:
                pass

        chrome.close()
        return True

    def _remove_envelope(self, xml):
        # type: (str) -> str
        if xml.index("<Envelope ") != 0:
            return xml

        index = xml.index("<Body>")
        ret_xml = xml[index + 6:]

        start_index = ret_xml.index(">")
        end_index = ret_xml.rindex("</Body>")
        end_index = ret_xml.rindex("</", 0, end_index)

        ret_xml = ret_xml[start_index + 1:end_index]

        return ret_xml



    def _get_request_index(self, path):
        for i in range(0, len(self.received_requests)):
            if path == self.received_requests[i].path:
                return i

        return -1


class NotifyListenersSefazHandler(object):
    __metaclass__ = ABCMeta

    ServerListeners = None

    @classmethod
    def add_notify_listeners(cls, listener):
        if NotifyListenersSefazHandler.ServerListeners is None:
            NotifyListenersSefazHandler.ServerListeners = []

        NotifyListenersSefazHandler.ServerListeners.append(listener)

    def notify_listeners(self, path, body):
        if NotifyListenersSefazHandler.ServerListeners:
            for server_listener in NotifyListenersSefazHandler.ServerListeners:  # type: RequestListener
                server_listener.request_received(path, body)


class FixedResponseSefazHttpHandler(http.server.BaseHTTPRequestHandler, NotifyListenersSefazHandler):
    Response = None

    def do_POST(self):
        body = ""
        if "Content-Length" in self.headers:
            content_length = int(self.headers["Content-Length"])
            if content_length > 0:
                body = self.rfile.read(content_length)

        self.notify_listeners(self.path, body)

        self.send_response(200)
        self.send_header("Content-Type", "application/xml; charset=utf-8")
        self.end_headers()

        if FixedResponseSefazHttpHandler.Response:
            self.wfile.write(FixedResponseSefazHttpHandler.Response)
