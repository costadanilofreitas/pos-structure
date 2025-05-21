from helper import ExtendedEnum
from messagebus import TokenCreator, TokenPriority

MESSAGE_GROUP = "112"


class ListenedTokens(ExtendedEnum):
    TK_NDISCOUNT_ADD_BENEFIT = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "1")
    TK_NDISCOUNT_REMOVE = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "2")
    TK_NDISCOUNT_VERIFY_AND_REMOVE = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "3")
    TK_NDISCOUNT_APPLY_PROMOTION_TENDERS = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "4")
    TK_NDISCOUNT_CHECK_STORED_BENEFIT = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "5")
