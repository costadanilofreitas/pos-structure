from ._TokenCreator import TokenCreator
from ._TokenPriority import TokenPriority


class DefaultToken(object):
    TK_SYS_ACK = TokenCreator.create_token(TokenPriority.high, "01", "1")
    TK_SYS_NAK = TokenCreator.create_token(TokenPriority.high, "01", "2")
    TK_EVT_EVENT = TokenCreator.create_token(TokenPriority.high, "04", "1")
