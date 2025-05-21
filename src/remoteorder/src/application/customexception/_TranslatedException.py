# -*- coding: utf-8 -*-
from sysactions import translate_message


class TranslatedException(Exception):
    def __init__(self, message, model=None):
        super(TranslatedException, self).__init__()
        self.message = self.error_message = self._translate_message(model, message)

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
