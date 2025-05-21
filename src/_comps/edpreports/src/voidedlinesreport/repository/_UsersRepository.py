from xml.etree import cElementTree as eTree

import sysactions
from msgbus import MBEasyContext
from old_helper import BaseRepository

USERS_CACHE = {}


class UsersRepository(BaseRepository):

    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        super(UsersRepository, self).__init__(mbcontext)

    @staticmethod
    def get_operators_name(voided_lines):
        for line in voided_lines:
            if line.operator in USERS_CACHE:
                line.operator_name = USERS_CACHE[line.operator]
                continue
            user_informations = sysactions.get_user_information(line.operator)
            if user_informations:
                user_name = eTree.XML(user_informations).find(".//user").get("UserName")
                line.operator_name = USERS_CACHE[line.operator] = user_name

        return voided_lines
