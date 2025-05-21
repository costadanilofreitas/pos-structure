# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from chatservice.model import Message, MessageFrom
from msgbus import MBEasyContext
from old_helper import BaseRepository
from persistence import Connection
from typing import List


class MessageRepository(BaseRepository):
    DatabaseDateFormat = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        super(MessageRepository, self).__init__(mb_context)
    
    def get_updates(self, message_id):
        # type: (int) -> List[Message]
        
        def inner_func(conn):
            # type: (Connection) -> List[Message]
            
            query = "SELECT Id, Origin, CreatedTime, ReceivedTime, Text " \
                    "FROM ChatMessages " \
                    "WHERE Id > {0} " \
                    "ORDER BY Id".format(message_id)
            unread_messages_tuples = [(int(x.get_entry(0)),
                                       x.get_entry(1).decode("utf-8"),
                                       x.get_entry(2).decode("utf-8"),
                                       x.get_entry(3).decode("utf-8") if x.get_entry(3) is not None else None,
                                       x.get_entry(4).decode("utf-8"))
                                      for x in conn.select(query)]
            
            unread_messages = self._convert_tuple_to_messages(unread_messages_tuples)
            
            return unread_messages
        
        return self.execute_with_connection(inner_func, service_name="DeliveryPersistence")
    
    def get_last_messages(self, quantity):
        # type: (int) -> List[Message]
        
        def inner_func(conn):
            # type: (Connection) -> List[Message]
            
            query = "SELECT Id, Origin, CreatedTime, ReceivedTime, Text " \
                    "FROM ChatMessages " \
                    "ORDER BY Id DESC " \
                    "LIMIT {0}".format(quantity)
            last_messages_tuples = [(int(x.get_entry(0)),
                                     x.get_entry(1).decode("utf-8"),
                                     x.get_entry(2).decode("utf-8"),
                                     x.get_entry(3).decode("utf-8") if x.get_entry(3) is not None else None,
                                     x.get_entry(4)) for x in conn.select(query)]
            
            return self._convert_tuple_to_messages(last_messages_tuples)
        
        return self.execute_with_connection(inner_func, service_name="DeliveryPersistence")
    
    def save_new_messages_from_store(self, messages):
        # type: (List[Message]) -> List[int]
        
        def inner_func(conn):
            # type: (Connection) -> List[int]
            
            ret = []  # type: List[int]
            for message in messages:
                # noinspection SqlInsertValues
                conn.query("INSERT INTO ChatMessages (Origin, CreatedTime, Text, LastTimeSentToServer) "
                           "VALUES ('{0}', '{1}', '{2}', '{3}')"
                           .format(MessageFrom.STORE,
                                   message.created_time.strftime(self.DatabaseDateFormat),
                                   message.text.replace("'", "''").encode("utf-8"),
                                   datetime.utcnow().strftime(self.DatabaseDateFormat)))
                
                new_id = [int(x.get_entry(0)) for x in conn.select("SELECT LAST_INSERT_ROWID()")][0]
                ret.append(new_id)
            
            return ret
        
        return self.execute_with_transaction(inner_func, service_name="DeliveryPersistence")
    
    def save_new_messages_from_sac(self, messages):
        # type: (List[Message]) -> List[Message]
        
        def inner_func(conn):
            # type: (Connection) -> List[Message]
            
            ret = []  # type: List[Message]
            for message in messages:
                ret_message = Message()
                ret_message.id = message.server_id
                
                select_query = "SELECT ReceivedTime FROM ChatMessages where ServerId = '{0}'".format(message.server_id)
                has_message_on_db = [x.get_entry(0).decode("utf-8") for x in conn.select(select_query)]
                if len(has_message_on_db) == 0:
                    # noinspection SqlInsertValues
                    insert_query = "INSERT INTO ChatMessages (Origin, CreatedTime, ReceivedTime, Text, ServerId) " \
                                   "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')" \
                        .format(message.message_from,
                                message.created_time.strftime(self.DatabaseDateFormat),
                                message.received_time.strftime(self.DatabaseDateFormat),
                                message.text.encode("utf-8"),
                                message.server_id.encode("utf-8"))
                    
                    conn.query(insert_query)
                    
                    ret_message.received_time = message.received_time
                else:
                    ret_message.received_time = datetime.strptime(has_message_on_db[0], self.DatabaseDateFormat)
                
                ret.append(ret_message)
            
            return ret
        
        return self.execute_with_transaction(inner_func, service_name="DeliveryPersistence")
    
    def mark_messages_received(self, messages):
        # type: (List[Message]) -> None
        
        def inner_func(conn):
            # type: (Connection) -> None
            
            for message in messages:
                conn.query("UPDATE ChatMessages SET ReceivedTime = '{0}' WHERE Id = {1}"
                           .format(message.received_time.strftime(self.DatabaseDateFormat), message.id))
        
        self.execute_with_transaction(inner_func, service_name="DeliveryPersistence")
    
    def get_messages_without_confirmation(self):
        # type: () -> List[Message]
        
        def inner_func(conn):
            # type: (Connection) -> List[Message]
            
            sync_date = datetime.utcnow() - timedelta(seconds=30)
            query = "SELECT Id, CreatedTime, Text " \
                    "FROM ChatMessages " \
                    "WHERE LastTimeSentToServer < '{0}' AND Origin = 'Store' AND ReceivedTime IS NULL " \
                    "ORDER BY Id".format(sync_date.strftime(self.DatabaseDateFormat))
            
            messages_without_confirmation = [(int(x.get_entry(0)),
                                              x.get_entry(1).decode("utf-8"),
                                              x.get_entry(2).decode("utf-8"))
                                             for x in conn.select(query)]
            
            messages = []
            for message_tuple in messages_without_confirmation:
                message = Message()
                message.id = message_tuple[0]
                message.created_time = datetime.strptime(message_tuple[1], self.DatabaseDateFormat)
                message.text = message_tuple[2]
                
                messages.append(message)
            
            return messages
        
        return self.execute_with_connection(inner_func, service_name="DeliveryPersistence")
    
    def _convert_tuple_to_messages(self, messages_tuples):
        # type: (List[tuple]) -> List[Message]
        
        messages = []
        for message_tuple in messages_tuples:
            unread_message = Message()
            unread_message.id = message_tuple[0]
            unread_message.message_from = message_tuple[1]
            unread_message.created_time = datetime.strptime(message_tuple[2], self.DatabaseDateFormat)
            unread_message.received_time = datetime.strptime(message_tuple[3], self.DatabaseDateFormat) \
                if message_tuple[3] is not None else None
            unread_message.text = message_tuple[4]
            
            messages.append(unread_message)
        
        return sorted(messages, key=lambda x: x.id)
