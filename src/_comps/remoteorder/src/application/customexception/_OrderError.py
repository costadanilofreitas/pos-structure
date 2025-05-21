# -*- coding: utf-8 -*-
from sysactions import translate_message


class OrderError(Exception):
    def __init__(self, remote_order_id, error_code, error_message, error_type=None, model=None):
        super(OrderError, self).__init__()
        self.remote_order_id = remote_order_id
        self.error_code = error_code
        self.message = self.error_message = self._translate_message(model, error_message)
        self.error_type = error_type

    def __str__(self):
        # type: () -> unicode
        return u"OrderError - Code: {} / Message: {}".format(self.error_code, self.error_message)

    @staticmethod
    def _translate_message(model, message):
        try:
            if model and message:
                split_message = message.replace('$', "").split("|")
                message = split_message[0]
                params = split_message[1:] if len(split_message) > 1 else []
                message = translate_message(model, message).format(*params)
        except Exception as _:
            pass

        return message
