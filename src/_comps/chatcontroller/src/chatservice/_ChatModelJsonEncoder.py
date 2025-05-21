# -*- coding: utf-8 -*-

from datetime import datetime
from json import JSONEncoder

from chatservice.model import Message


class ChatModelJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            ret_dict = {}
            if obj.id is not None:
                ret_dict["id"] = obj.id
            if obj.message_from is not None:
                ret_dict["from"] = obj.message_from
            if obj.created_time is not None:
                ret_dict["createdTime"] = obj.created_time
            if obj.received_time is not None:
                ret_dict["receivedTime"] = obj.received_time
            if obj.text is not None:
                ret_dict["text"] = obj.text
            if obj.server_id is not None:
                ret_dict["serverId"] = obj.server_id

            return ret_dict

        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return super(ChatModelJsonEncoder, self).default(obj)
