from logging import Logger

from flask import Response
from mebuhi.event import SubscriberCreator


class StartListenProcessor(object):
    def __init__(self, subscriber, logger):
        # type: (SubscriberCreator, Logger) -> None
        self.subscriber = subscriber
        self.logger = logger

    def get_caller_ip(self, request):
        if not request.headers.getlist("X-Forwarded-For"):
            return request.remote_addr
        return request.headers.getlist("X-Forwarded-For")[0]

    def handle(self, path_parameters, request):
        caller_ip = self.get_caller_ip(request)
        self.logger.info("IP: {} Start handling Start".format(caller_ip))
        sync_id = None
        try:
            subject = request.args['subject'].encode("utf-8")
            sync_id = self.subscriber.create_subscriber(subject)
            return Response(status=200, headers={"x-sync-id": sync_id})
        finally:
            log_message = "IP: {} Finish handling Start - {}"
            self.logger.info(log_message.format(caller_ip, sync_id))
