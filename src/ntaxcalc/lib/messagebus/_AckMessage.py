from ._Message import Message
from ._DefaultToken import DefaultToken
from ._DataType import DataType


class AckMessage(Message):
    def __init__(self, data=None, data_type=None):
        if data is None:
            super(AckMessage, self).__init__(DefaultToken.TK_SYS_ACK)
        else:
            if data_type is None:
                super(AckMessage, self).__init__(DefaultToken.TK_SYS_ACK, DataType.json, data)
            else:
                super(AckMessage, self).__init__(DefaultToken.TK_SYS_ACK, data_type, data)
