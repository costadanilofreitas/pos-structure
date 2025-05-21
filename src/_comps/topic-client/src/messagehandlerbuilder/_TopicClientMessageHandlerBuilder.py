import logging
import boto3

from messagehandler import MessageHandlerBuilder
from messageprocessor import \
    MessageProcessorMessageHandler, \
    DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback
from topicclient.processor import ServerEventProcessor

logger = logging.getLogger("TopicClient")


class TopicClientMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self,
                 topic_arn,
                 endpoint_url,
                 region_name,
                 aws_access_key_id,
                 aws_secret_access_key,
                 subjects,
                 store_code,
                 context):
        self.topic_arn = topic_arn
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.subjects = subjects
        self.store_code = store_code
        self.context = context

        self.message_handler = None

    def build_singletons(self):
        client = boto3.client("sns",
                              aws_access_key_id=self.aws_access_key_id,
                              aws_secret_access_key=self.aws_secret_access_key,
                              region_name=self.region_name,
                              endpoint_url=self.endpoint_url)

        event_processors = {}
        for subject in self.subjects:
            server_event_processor = ServerEventProcessor(subject, self.store_code, self.context, client,
                                                          self.topic_arn)
            event_processors[subject] = server_event_processor

        callbacks = [LoggingProcessorCallback(logger)]
        self.message_handler = MessageProcessorMessageHandler(event_processors,
                                                              None,
                                                              None,
                                                              DefaultMessageProcessorExecutorFactory(callbacks),
                                                              logger)

    def build_message_handler(self):
        return self.message_handler

    def destroy_message_handler(self, message_handler):
        return

    def destroy_singletons(self):
        return
