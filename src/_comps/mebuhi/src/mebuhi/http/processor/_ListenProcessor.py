from logging import Logger

from flask import Response
from mebuhi.event import WaiterRetriever


class ListenProcessor(object):
    def __init__(self, waiter_retriever, logger):
        # type: (WaiterRetriever, Logger) -> None
        self.waiter_retriever = waiter_retriever
        self.logger = logger

    def get_caller_ip(self, request):
        if not request.headers.getlist("X-Forwarded-For"):
            return request.remote_addr
        return request.headers.getlist("X-Forwarded-For")[0]

    def handle(self, path_parameters, request):
        request_sync_id = request.values['syncId']
        caller_ip = self.get_caller_ip(request)
        self.logger.info("IP: {} Start handling SyncId - {}".format(caller_ip, request_sync_id))
        response_sync_id = None
        try:
            waiter = self.waiter_retriever.get_waiter(request_sync_id)
            if waiter is None:
                self.logger.info("No waiter with SyncId - Returning 500")
                return Response(status=500, headers={"x-out-of-sync": "true"})
            response_sync_id = waiter.get_sync_id()
            events = waiter.get_events()
            response = self.create_response_xml(events)
            headers = {"X-sync-id": response_sync_id}
            return Response(response, status=200, content_type="text/xml", headers=headers)
        finally:
            log_message = "IP: {} Finish handling SyncId - {} / {}"
            self.logger.info(log_message.format(caller_ip, request_sync_id, response_sync_id))

    def create_response_xml(self, events):
        event_xml = ""
        for event in events:
            event_xml += event.data
        return "<Events>{}</Events>".format(event_xml)
