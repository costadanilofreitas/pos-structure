from helper import ExtendedEnum
from messagebus import TokenCreator, TokenPriority

MESSAGE_GROUP = "95"


class ListenedTokens(ExtendedEnum):
    TK_POS_UPDATER_PERFORM_CATALOG_UPDATE = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "1")
    TK_POS_UPDATER_PERFORM_MEDIA_UPDATE = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "2")
    TK_POS_UPDATER_PERFORM_USER_UPDATE = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "3")
    TK_POS_GET_CATALOG_VERSION_TO_APPLY = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "4")
    TK_POS_UPDATER_PERFORM_LOADER_UPDATE = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP, "5")
