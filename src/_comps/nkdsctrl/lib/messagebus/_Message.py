from typing import Optional, Any
from ._DataType import DataType


class Message(object):
    def __init__(self, token, data_type=DataType.empty, data=None, timeout=-1):
        # type: (int, int, Optional[Any], int) -> None
        self.token = token
        self.data_type = data_type
        self.data = data
        self.timeout = timeout
        self.imp_message = None  # type: Any
