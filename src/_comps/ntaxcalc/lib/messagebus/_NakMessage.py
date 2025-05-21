from ._Message import Message
from ._DefaultToken import DefaultToken
from ._DataType import DataType


class NakMessage(Message):
    def __init__(self, data=None, data_type=None):
        if data is None:
            super(NakMessage, self).__init__(DefaultToken.TK_SYS_NAK)
        else:
            if data_type is None:
                super(NakMessage, self).__init__(DefaultToken.TK_SYS_NAK, DataType.json, data)
            else:
                super(NakMessage, self).__init__(DefaultToken.TK_SYS_NAK, data_type, data)
