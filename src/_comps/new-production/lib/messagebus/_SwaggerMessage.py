import json

from typing import Dict

from ._Message import Message
from ._DataType import DataType
from ._DefaultToken import DefaultToken


class SwaggerMessage(Message):
    def __init__(self, status_code, body=None, headers=None):
        # type: (int, str, Dict[str, str]) -> None
        self.status_code = status_code
        self.body = body
        self.headers = headers

        super(SwaggerMessage, self).__init__(DefaultToken.TK_SYS_ACK, DataType.swagger, b"")
