# -*- coding: utf-8 -*-

import datetime
import json
import sys

import iso8601
import six
from chatservice.model import Message, MessageFrom
from chatservice.customexception import InvalidJsonException
from typing import List, Dict


class MessageParser(object):
    
    def parse(self, input_json):
        # type: (unicode) -> Message
        
        try:
            message_json = json.loads(input_json)
        except ValueError as ex:
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        try:
            self._validate_json_structure(message_json)
            return self._parse_message(message_json)
        except InvalidJsonException as ex:
            six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

    def parse_sac_messages(self, input_json):
        # type: (unicode) -> List[Message]
        
        try:
            messages_json = json.loads(input_json)
        except ValueError as ex:
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        try:
            if not isinstance(messages_json, list):
                raise InvalidJsonException("The json should be a list")

            messages = []
            for message_json in messages_json:
                self._validate_sac_json_structure(message_json)
                message = self._parse_sac_message(message_json)
                messages.append(message)

            return messages
        except InvalidJsonException as ex:
            six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

    def parse_sac_ack_messages(self, input_json):
        # type: (unicode) -> List[Message]
        
        try:
            messages_json = json.loads(input_json)
        except ValueError as ex:
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        try:
            if not isinstance(messages_json, list):
                raise InvalidJsonException("The json should be a list")

            messages = []
            for message_json in messages_json:
                self._validate_sac_ack_json_structure(message_json)
                message = self._parse_sac_ack_message(message_json)
                messages.append(message)

            return messages
        except InvalidJsonException as ex:
            six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

    @staticmethod
    def _validate_json_structure(message_json):
        # type: (Dict) -> None
        
        if "text" not in message_json:
            raise InvalidJsonException("Json without 'text' tag")

        if message_json["text"] == "":
            raise InvalidJsonException("The 'text' field cannot be empty")

    @staticmethod
    def _validate_sac_json_structure(message_json):
        # type: (Dict) -> None
        
        if "id" not in message_json:
            raise InvalidJsonException("Json without 'id' tag")

        if "text" not in message_json:
            raise InvalidJsonException("Json without 'text' tag")

        if "createdTime" not in message_json:
            raise InvalidJsonException("Json without 'createdTime' tag")

        try:
            iso8601.parse_date(message_json["createdTime"])
        except iso8601.ParseError:
            raise InvalidJsonException("Invalid 'createTime': " + message_json["createTime"])

    @staticmethod
    def _validate_sac_ack_json_structure(message_json):
        # type: (Dict) -> None
        
        if "id" not in message_json:
            raise InvalidJsonException("Json without 'id' tag")

        if "receivedTime" not in message_json:
            raise InvalidJsonException("Json without 'receivedTime' tag")

        try:
            iso8601.parse_date(message_json["receivedTime"])
        except iso8601.ParseError:
            raise InvalidJsonException("Invalid 'createTime': " + message_json["receivedTime"])

    @staticmethod
    def _parse_message(message_json):
        # type: (Dict) -> Message
        
        message = Message()
        message.id = None
        message.text = message_json.get("text")
        message.message_from = MessageFrom.STORE
        message.created_time = datetime.datetime.utcnow()
        message.received_time = None
        message.server_id = None

        return message

    @staticmethod
    def _parse_sac_message(message_json):
        # type: (Dict) -> Message
        
        message = Message()
        message.id = None
        message.text = message_json["text"]
        message.server_id = message_json["id"]
        message.message_from = MessageFrom.SAC
        message.created_time = iso8601.parse_date(message_json["createdTime"])
        message.received_time = datetime.datetime.utcnow()

        return message

    @staticmethod
    def _parse_sac_ack_message(message_json):
        # type: (Dict) -> Message
        
        message = Message()
        message.id = message_json["id"]
        message.text = None
        message.server_id = None
        message.message_from = MessageFrom.SAC
        message.created_time = None
        message.received_time = iso8601.parse_date(message_json["receivedTime"])

        return message
