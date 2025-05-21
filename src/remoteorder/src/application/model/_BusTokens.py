from messagebus import TokenCreator, TokenPriority


class BusTokens(object):
    # FiscalWrapper
    TK_FISCALWRAPPER_CANCEL_ORDER = TokenCreator.create_token(TokenPriority.low, "31", "10")
    TK_FISCALWRAPPER_PROCESS_REQUEST = TokenCreator.create_token(TokenPriority.high, "31", "1")
    TK_FISCALWRAPPER_GET_FISCAL_XML = TokenCreator.create_token(TokenPriority.low, "31", "18")

    # Rupture
    TK_RUPTURA_GET_DISABLED = TokenCreator.create_token(TokenPriority.low, "42", "4")
    TK_RUPTURA_GET_CLEAN_TIME_WINDOW = TokenCreator.create_token(TokenPriority.low, "42", "10")

    # Blacklist
    TK_BLACKLIST_FILTER_STRING = TokenCreator.create_token(TokenPriority.low, "44", "1")

    # Production
    TK_PROD_GET_ORDER_MAX_PREP_TIME = TokenCreator.create_token(TokenPriority.low, "C", "3")

    # RemoteOrder
    TK_REMOTE_ORDER_GET_STORED_ORDERS = TokenCreator.create_token(TokenPriority.low, "37", "1")
    TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION = TokenCreator.create_token(TokenPriority.low, "37", "2")
    TK_REMOTE_ORDER_GET_STORE = TokenCreator.create_token(TokenPriority.low, "37", "3")
    TK_REMOTE_ORDER_CLOSE_STORE = TokenCreator.create_token(TokenPriority.low, "37", "4")
    TK_REMOTE_ORDER_OPEN_STORE = TokenCreator.create_token(TokenPriority.low, "37", "5")
    TK_REMOTE_ORDER_INVALID_ORDER_ID = TokenCreator.create_token(TokenPriority.low, "37", "100")
    TK_REMOTE_STORE_ALREADY_OPEN = TokenCreator.create_token(TokenPriority.low, "37", "101")
    TK_REMOTE_STORE_ALREADY_CLOSED = TokenCreator.create_token(TokenPriority.low, "37", "102")
    TK_REMOTE_ORDER_REPRINT = TokenCreator.create_token(TokenPriority.low, "37", "104")
    TK_REMOTE_ORDER_GET_AVAILABLE_PRODUCTS = TokenCreator.create_token(TokenPriority.low, "37", "201")
    TK_REMOTE_ORDER_GET_UNAVAILABLE_PRODUCTS = TokenCreator.create_token(TokenPriority.low, "37", "202")
    TK_REMOTE_ORDER_UPDATE_AVAILABLE_PRODUCTS = TokenCreator.create_token(TokenPriority.low, "37", "203")
    TK_REMOTE_ORDER_ERROR = TokenCreator.create_token(TokenPriority.low, "37", "204")
    TK_REMOTE_ORDER_CHECK_RUPTURA_DIFF_ITEMS = TokenCreator.create_token(TokenPriority.low, "37", "205")
    TK_REMOTE_ORDER_VOID_REMOTE_ORDER = TokenCreator.create_token(TokenPriority.low, "37", "206")
    TK_REMOTE_ORDER_CREATE_AND_PRODUCE = TokenCreator.create_token(TokenPriority.low, "37", "207")
    TK_REMOTE_ORDER_CREATE = TokenCreator.create_token(TokenPriority.low, "37", "208")
    TK_REMOTE_ORDER_GET_VOIDED_ORDERS = TokenCreator.create_token(TokenPriority.low, "37", "209")
    TK_REMOTE_ORDER_GET_POS_ID = TokenCreator.create_token(TokenPriority.low, "37", "210")
    TK_REMOTE_ORDER_GET_CONFIRMED_ORDERS = TokenCreator.create_token(TokenPriority.low, "37", "211")
    TK_REMOTE_ORDER_GET_RUPTURED_ITEMS = TokenCreator.create_token(TokenPriority.low, "37", "213")
    TK_REMOTE_ORDER_GET_STORE_STATUS = TokenCreator.create_token(TokenPriority.low, "37", "214")
    TK_REMOTE_ORDER_CHECK_IF_ORDER_EXISTS = TokenCreator.create_token(TokenPriority.low, "37", "215")
    TK_REMOTE_ORDER_REPRINT_DELIVERY = TokenCreator.create_token(TokenPriority.low, "37", "216")
    TK_REMOTE_ORDER_GET_LOGISTIC_PARTNERS = TokenCreator.create_token(TokenPriority.low, "37", "217")
    TK_REMOTE_ORDER_SEARCH_LOGISTIC = TokenCreator.create_token(TokenPriority.low, "37", "218")
    TK_REMOTE_ORDER_SEND_ORDER_TO_LOGISTIC = TokenCreator.create_token(TokenPriority.low, "37", "219")
    TK_REMOTE_ORDER_CANCEL_LOGISTIC = TokenCreator.create_token(TokenPriority.low, "37", "220")
    TK_REMOTE_ORDER_SAVE_ORDER = TokenCreator.create_token(TokenPriority.low, "37", "221")
    TK_REMOTE_ORDER_GET_DELIVERY_FEE_CODE = TokenCreator.create_token(TokenPriority.low, "37", "222")
    TK_REMOTE_ORDER_CONFIRM_DELIVERY_PAYMENT = TokenCreator.create_token(TokenPriority.low, "37", "223")
    TK_REMOTE_ORDER_CHECK_IF_DELIVERY_FEE_IS_ENABLED = TokenCreator.create_token(TokenPriority.low, "37", "224")
