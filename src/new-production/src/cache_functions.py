from xml.etree import cElementTree as eTree
from threading import Thread, Condition

from msgbus import TK_USERCTRL_GETINFO
from messagebus import Message

from production.model import User


class UsersInfoCache(Thread):
    def __init__(self, message_bus, logger):
        super(UsersInfoCache, self).__init__()

        self.message_bus = message_bus
        self.logger = logger

        self.users_information = {}

        self.running = True
        self.sleep_condition = Condition()
        self.sleep_time = 300

    def stop(self):
        self.running = False
        with self.sleep_condition:
            self.sleep_condition.notify_all()

    def sleep(self, time):
        with self.sleep_condition:
            self.sleep_condition.wait(time)

    def run(self):
        while self.running:
            self.renew_cache()
            self.sleep(self.sleep_time)

    def renew_cache(self):
        try:
            users = {}
            message = Message(TK_USERCTRL_GETINFO, timeout=30000000)
            response = self.message_bus.send_message("BOSS", message)
            for user in eTree.XML(response.data).findall("user"):
                user_id = user.get("UserId")
                user_name = user.get("LongName")
                user_level = user.get("Level")
                users[user_id] = User(user_id, user_name, user_level)

            self.users_information = users
        except Exception as _:
            self.users_information = {}

    def get_users_info(self):
        if not self.users_information:
            self.renew_cache()

        return self.users_information
