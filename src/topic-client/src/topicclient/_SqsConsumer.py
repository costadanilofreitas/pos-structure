import logging

from messagebus import Event


logger = logging.getLogger("TopicClientReceiveThread")


class SqsConsumer(object):
    def __init__(self, message_bus, queue, store_code):
        self.message_bus = message_bus
        self.queue = queue
        self.store_code = store_code
        self.running = True

        logger.info("Starting sqs consumer...")

    def run(self):
        while self.running:
            try:
                messages = self.queue.receive_messages(AttributeNames=['All'],
                                                       MaxNumberOfMessages=10,
                                                       MessageAttributeNames=['ToStore', 'Subject'],
                                                       VisibilityTimeout=5,
                                                       WaitTimeSeconds=20)

                if len(messages) != 0:
                    logger.info("Received messages: {}".format(len(messages)))
                    
                for message in messages:
                    message.delete()

                    try:
                        if message.message_attributes is None:
                            logger.error("Message without attributes: {}".format(message))
                            continue

                        if "ToStore" not in message.message_attributes:
                            logger.error("Message without ToStore: {}".format(message))
                            continue

                        to_store = message.message_attributes["ToStore"]
                        if "StringValue" not in to_store:
                            logger.error("Message without ToStore value: {}".format(message))
                            continue

                        to_store_value = to_store["StringValue"]
                        index = to_store_value.find("_")
                        if index < 0:
                            store_code = to_store_value
                        else:
                            store_code = to_store_value[index + 1:]

                        if store_code != str(self.store_code):
                            logger.error("Message not for this store: {}".format(message))
                            continue

                        if "Subject" not in message.message_attributes:
                            logger.error("Message without subject: {}".format(message))
                            continue

                        if "StringValue" not in message.message_attributes["Subject"]:
                            logger.error("Message without subject value: {}".format(message))
                            continue

                        event = Event(message.message_attributes["Subject"]["StringValue"],
                                      "",
                                      message.body.encode("utf-8"))
                        logger.info("Publishing event: {} - {}".format(event.subject, event.data))
                        self.message_bus.publish_event(event)
                    except Exception as _: # noqa
                        logger.exception("Error publishing event")
            except Exception as _: # noqa
                logger.exception("Error receiving messages")

    def stop(self):
        logger.info("Stopping sqs consumer...")
        
        self.running = False
