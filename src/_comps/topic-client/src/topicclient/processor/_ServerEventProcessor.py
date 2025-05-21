import logging

from abc import ABCMeta

from messageprocessorutil import UuidMessageProcessor


logger = logging.getLogger("TopicClient")


class ServerEventProcessor(UuidMessageProcessor):
    __metaclass__ = ABCMeta

    def __init__(self, event_name, store_code, context, sns_client, topic_arn):
        super(ServerEventProcessor, self).__init__(event_name)
        self.store_code = store_code
        self.context = context
        self.sns_client = sns_client
        self.topic_arn = topic_arn

    def parse_data(self, data):
        return data

    def call_business(self, obj):
        return obj

    def format_response(self, message_bus, message, event, data, result):
        subject = event.subject
        message_attributes = {
            "Subject": {
                "DataType": "String",
                "StringValue": subject
            },
            "FromStore": {
                "DataType": "String",
                "StringValue": self.store_code
            }
        }
        if self.context is not None:
            message_attributes["Context"] = {
                "DataType": "String",
                "StringValue": self.context
            }

        response = self.sns_client.publish(TopicArn=self.topic_arn,
                                           Message=data,
                                           Subject=event.subject,
                                           MessageAttributes=message_attributes)

        if "MessageId" not in response or response["MessageId"] is None or response["MessageId"] == "":
            logger.info("MessageId not found on the response")

    def format_exception(self, message_bus, message, event, input_obj, exception):
        return

    def format_parse_exception(self, message_bus, message, event, data, exception):
        return
