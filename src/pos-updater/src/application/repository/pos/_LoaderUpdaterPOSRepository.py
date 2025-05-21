# -*- coding: utf-8 -*-

import sqlite3

from datetime import datetime

from application.model import UpdateType, UserUpdateData, Payment, UpdateStatus
from application.model.configuration import Configurations
from application.model.customexception import ErrorInsertingNewUpdateVersion, ErrorRestartingHV
from mbcontextmessagehandler import MbContextMessageBus
from msgbus import TK_HV_GLOBALRESTART, TK_SYS_ACK
from mwhelper import BaseRepository


class LoaderUpdaterPOSRepository(BaseRepository):
    def __init__(self, message_bus, configs):
        # type: (MbContextMessageBus, Configurations) -> None

        super(LoaderUpdaterPOSRepository, self).__init__(message_bus.mbcontext)

        self.message_bus = message_bus
        self.configs = configs
        self.update_type = UpdateType.loader
        self.update_value = self.update_type.value
        self.local_configs = configs.updaters[self.update_type.name]
        
    def delete_all_payments(self, database_path):
        # type: (str) -> None
        
        sql = """DELETE FROM TenderType"""
        conn = self._create_connection(database_path)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    
    def insert_payments(self, database_path, payments):
        # type: (str, List[Payment]) -> None

        conn = self._create_connection(database_path)
        cur = conn.cursor()
        
        for payment in payments:
            sql = """
            INSERT INTO TenderType VALUES
            ({}, '{}', '{}', NULL, 0, NULL, {}, {}, {}, 0, {})
            """.format(payment.payment_id, payment.name, payment.currency, payment.change_limit,
                       payment.electronic_type, payment.open_drawer, payment.parent_id or "NULL")
    
            cur.execute(sql)
            
        conn.commit()

    def insert_new_loader_update(self, update_id, update_name):
        # type: (str, str) -> None
    
        try:
            def inner_func(conn):
                # type: (Connection) -> None
            
                date_now = str(datetime.now().isoformat())
                query = """
                INSERT INTO UpdatesController
                (UpdateId, UpdateName, TypeId, StatusId, ObtainedDate, DownloadedDate, BackupDate, AppliedDate,
                NotifiedDate)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{4}', '{4}', '{4}', '{4}')"""
                query_format = query.format(update_id, update_name, self.update_value, UpdateStatus.applied, date_now)
                conn.query(query_format)
        
            self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)
        except Exception as ex:
            raise ErrorInsertingNewUpdateVersion(ex)

    def get_last_loader_update_id(self):
        # type: () -> int
    
        def inner_func(conn):
            # type: (Connection) -> int
        
            query = """
                SELECT UpdateId
                FROM UpdatesController
                WHERE TypeId = '{}' AND AppliedDate IS NOT NULL
                ORDER BY Id DESC
                LIMIT 1""".format(self.update_value)
        
            cursor = conn.select(query)
            row = cursor.get_row(0)
        
            if row:
                update_id = row.get_entry("UpdateId")
                return int(update_id)
        
            return 0
    
        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def some_update_already_applied(self):
        # type: () -> bool
    
        def inner_func(conn):
            # type: (Connection) -> bool
        
            query = """SELECT COUNT(*) as VersionsApplied
                       FROM UpdatesController
                       WHERE TypeId = '{0}' AND AppliedDate IS NOT NULL
                    """.format(self.update_value)
        
            cursor = conn.select(query)
            row = cursor.get_row(0)
        
            if row:
                versions_applied = row.get_entry("VersionsApplied")
                return int(versions_applied) > 0
        
            return False
    
        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)
    
    def restart_hv(self):
        # type: () -> None
        res = self.message_bus.mbcontext.MB_SendMessage(self.message_bus.mbcontext.hv_service, TK_HV_GLOBALRESTART)
        if res.token != TK_SYS_ACK:
            raise ErrorRestartingHV("Could not perform HV global restart")
        
    @staticmethod
    def _create_connection(db_file):
        return sqlite3.connect(db_file)
