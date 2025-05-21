from helper import ExtendedEnum
from messagebus import TokenCreator, TokenPriority

MESSAGE_GROUP = "113"


class ListenedTokens(ExtendedEnum):

    TK_NCOUPON_APPLY_COUPON = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "1")
    TK_NCOUPON_UNLOCK_COUPON = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "2")
    TK_NCOUPON_BURN_COUPON = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "3")
    TK_NCOUPON_GET_COUPON_INFO = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "4")
