# -*- coding: utf-8 -*-

from mwhelper import BaseRepository
from persistence import Connection
from typing import Union

from application.model import StoreStatusHistory


class StoreRepository(BaseRepository):
    def __init__(self, mb_context):
        super(StoreRepository, self).__init__(mb_context)
        self.mb_context = mb_context

    def add_store_status(self, status, operator):
        # type: (unicode, unicode) -> None
        def inner_func(conn):
            # type: (Connection) -> None
            conn.query("INSERT INTO StoreStatusHistory (Status, SentToServer, Operator) VALUES ('{0}', {1}, {2})".format(status, 0, operator))

        self.execute_with_connection(inner_func, service_name="DeliveryPersistence")

    def get_current_store_status(self):
        # type: () -> unicode
        def inner_func(conn):
            # type: (Connection) -> StoreStatusHistory
            
            status = [(x.get_entry(0), x.get_entry(1).encode("utf-8"), x.get_entry(2)) for x in conn.select("select Id, Status, Operator from StoreStatusHistory order by Id desc limit 1")]

            ret = StoreStatusHistory()
            
            if len(status) == 0:
                conn.query("INSERT INTO StoreStatusHistory (Status, SentToServer) VALUES ('{0}', {1})".format("Open", 0))
                
                ret.id = 0
                ret.status = "Open"
                ret.operator = 0
            else:
                ret.id = int(status[0][0])
                ret.status = status[0][1]
                ret.operator = status[0][2]
                
            return ret

        return self.execute_with_connection(inner_func, service_name="DeliveryPersistence")

    def get_not_sent_status(self):
        # type: () -> Union[StoreStatusHistory, None]
        def inner_func(conn):
            # type: (Connection) -> Union[StoreStatusHistory, None]
            status = [(x.get_entry(0), x.get_entry(1).encode("utf-8"), x.get_entry(2)) for x in conn.select("select Id, Status, Operator from StoreStatusHistory where SentToServer = 0 order by Id desc limit 1")]

            if len(status) == 0:
                return None

            ret = StoreStatusHistory()
            ret.id = int(status[0][0])
            ret.status = status[0][1]
            ret.operator = status[0][2]

            return ret

        return self.execute_with_connection(inner_func, service_name="DeliveryPersistence")

    def mark_status_sent(self, status_id):
        # type: (int) -> None
        def inner_func(conn):
            # type: (Connection) -> None
            conn.query("UPDATE StoreStatusHistory set SentToServer = 1 where Id = {0}".format(status_id))

        self.execute_with_connection(inner_func, service_name="DeliveryPersistence")
