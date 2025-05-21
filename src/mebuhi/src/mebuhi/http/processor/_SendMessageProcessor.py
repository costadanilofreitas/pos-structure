import base64

from flask import Response, Request
from messagebus import Message
from typing import Dict


class SendMessageProcessor(object):
    def __init__(self, message_bus, logger):
        self.message_bus = message_bus
        self.logger = logger

    def handle(self, path_parameters, request):
        # type: (Dict[str, str], Request) -> Response
        service_name = path_parameters['serviceName']
        token_request = request.args['token']
        if token_request == "TK_POS_EXECUTEACTION":
            token_request = int("0xF0500003", 16)
        else:
            token_request = int(token_request, 16)

        format_request = int(request.args['format'])
        if 'timeout' in request.args:
            timeout_request = int(request.args['timeout']) * 1000
        else:
            timeout_request = -1
        is_base_64_request = request.args['isBase64']
        if 'payload' in request.args:
            body_request = request.args['payload']
        else:
            body_request = request.get_data(parse_form_data=False)

        try:
            if is_base_64_request == 'true' and len(body_request) > 0:
                body_request = base64.b64decode(body_request)

            message = Message(int(token_request), int(format_request), body_request, int(timeout_request))
            reply = self.message_bus.send_message(service_name, message)

            return Response(reply.data, status=200, content_type="text/xml")
        except Exception as err:
            if self.logger:
                self.logger.exception("Request from {} - Error sending Message".format(request.remote_addr))
            return Response(err, status=400)
