from messagebus import TokenCreator, TokenPriority


class NDiscountTokens(object):
    NDISCOUNT_MESSAGE_GROUP = "112"

    TK_NDISCOUNT_ADD_BENEFIT = TokenCreator.create_token(TokenPriority.low, NDISCOUNT_MESSAGE_GROUP, "1")
    TK_NDISCOUNT_REMOVE = TokenCreator.create_token(TokenPriority.low, NDISCOUNT_MESSAGE_GROUP, "2")
    TK_NDISCOUNT_VERIFY_AND_REMOVE = TokenCreator.create_token(TokenPriority.low, NDISCOUNT_MESSAGE_GROUP, "3")
    TK_NDISCOUNT_APPLY_PROMOTION_TENDERS = TokenCreator.create_token(TokenPriority.low, NDISCOUNT_MESSAGE_GROUP, "4")
    TK_NDISCOUNT_CHECK_STORED_BENEFIT = TokenCreator.create_token(TokenPriority.low, NDISCOUNT_MESSAGE_GROUP, "5")


class LoyaltyTokens(object):
    LOYALTY_MESSAGE_GROUP = "111"

    TK_LOYALTY_GET_AND_LOCK_VOUCHER = TokenCreator.create_token(TokenPriority.low, LOYALTY_MESSAGE_GROUP, "2")
    TK_LOYALTY_BURN_VOUCHER = TokenCreator.create_token(TokenPriority.low, LOYALTY_MESSAGE_GROUP, "3")
    TK_LOYALTY_UNLOCK_VOUCHER = TokenCreator.create_token(TokenPriority.low, LOYALTY_MESSAGE_GROUP, "4")
