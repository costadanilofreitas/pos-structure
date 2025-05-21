import json
from messagebus import MessageBus, Event, Message, DataType, SwaggerMessage
from msgbus import MBEasyContext, MBMessage, FM_PARAM, FM_STRING, FM_XML


class MbContextMessageBus(MessageBus):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def publish_event(self, event):
        # type: (Event) -> Message
        data = event.data
        if data is None:
            data = ""

        if event.event_type is None:
            event.event_type = ""

        msg = self.mbcontext.MB_EasyEvtSend(subject=event.subject,
                                            type=event.event_type,
                                            xml=data,
                                            synchronous=False,
                                            sourceid=event.source,
                                            queue=None,
                                            timeout=event.timeout)
        return self._convert_mb_message_to_message(msg)

    def send_message(self, component, message):
        data = message.data
        if data is None:
            data = ""

        msg = self.mbcontext.MB_EasySendMessage(component, message.token, message.data_type, data, message.timeout)

        return self._convert_mb_message_to_message(msg)

    def subscribe(self, subject):
        subject_to_subscribe = ""
        if isinstance(subject, (list,)):
            subject_to_subscribe = " ".join(subject_to_subscribe)
        else:
            subject_to_subscribe = subject
        self.mbcontext.MB_EasyEvtSubscribe(subject_to_subscribe)

    def reply_message(self, message, reply_message):
        self._reply_mb_message(message.imp_message, reply_message)

    def reply_event(self, event, reply_message):
        self._reply_mb_message(event.imp_message, reply_message)

    def _reply_mb_message(self, msg, reply_message):
        # type: (MBMessage, Message) -> None
        msg.token = reply_message.token
        data = reply_message.data
        if reply_message.data is None:
            data = ""

        if isinstance(reply_message, SwaggerMessage):
            transformed_data = {
                "status": reply_message.status_code
            }

            if reply_message.body is not None:
                transformed_data["body"] = reply_message.body

            if reply_message.headers is not None:
                transformed_data["headers"] = reply_message.headers

            reply_message.data = transformed_data

        if isinstance(reply_message.data, dict):
            data = json.dumps(reply_message.data)

        self.mbcontext.MB_ReplyMessage(msg,
                                       format=reply_message.data_type,
                                       data=data)

    @staticmethod
    def _convert_mb_message_to_message(msg):
        # type: (MBMessage) -> Message
        data_format = msg.format
        data = msg.data
        if msg.format == FM_PARAM:
            if msg.data == "" or msg.data is None:
                data_format = DataType.empty
                data = None
            else:
                data_format = DataType.param
        elif msg.format == FM_XML:
            data_format = DataType.xml
        elif msg.format == FM_STRING:
            data_format = DataType.string

        return Message(msg.token, data_format, data)
