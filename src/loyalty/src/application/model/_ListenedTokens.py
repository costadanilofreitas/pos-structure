from helper import ExtendedEnum
from messagebus import TokenCreator, TokenPriority

MESSAGE_GROUP = "111"


class ListenedTokens(ExtendedEnum):
    TK_LOYALTY_GET_LOYALTY_ID = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "1")
    TK_LOYALTY_GET_AND_LOCK_VOUCHER = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "2")
    TK_LOYALTY_BURN_VOUCHER = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "3")
    TK_LOYALTY_UNLOCK_VOUCHER = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "4")
