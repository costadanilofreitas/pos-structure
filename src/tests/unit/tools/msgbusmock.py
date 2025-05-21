from ctypes import create_string_buffer

from msgbus import MBMessage, MBEasyContext

import mock


class FakePMessage(object):
    def __init__(self, contents):
        self.contents = contents


class FakeMessage(object):
    def __init__(self, token, data):
        self.sign = None
        if data is None:
            self.size = 0
            self.data = None
        else:
            data_bytes = data.decode("utf-8")
            self.size = len(data_bytes)
            self.data = create_string_buffer(data_bytes, self.size)
        self.token = token
        self.format = None
        self.destname = None
        self.data = data
        self.trailer = None
        self.crc = None
        self.remotehost = None


class MBMessageBuilder(object):
    def __init__(self):
        self.token = None
        self.data = None

    def with_token(self, token):
        self.token = token
        return self

    def with_data(self, data):
        self.data = data
        return self

    def build(self):
        return MBMessage(FakePMessage(FakeMessage(self.token, self.data)), autodel=False)


class MBEasyContextBuilder(object):
    def __init__(self):
        self.message_queue = None
        self.handled_tokens = []

    def with_message_queue(self, message_queue):
        self.message_queue = message_queue

        return self

    def build(self):
        mbcontext = mock.NonCallableMock(spec=MBEasyContext)

        if self.message_queue is not None:
            mbcontext.MB_EasyGetMessage = mock.Mock(side_effect=self.message_queue)


        return mbcontext
