from datetime import datetime

import msgbus
from application.model import UpdateType, CatalogUpdateData, UpdateStep, UpdateStatus
from application.model.configuration import Configurations
from application.model.customexception import \
    ErrorInsertingNewUpdateVersion, \
    ErrorUpdatingStep, \
    ErrorUpdatingStatus, \
    ErrorRestartingHV
from mbcontextmessagehandler import MbContextMessageBus
from msgbus import TK_HV_GLOBALRESTART
from mwhelper import BaseRepository
from persistence import Connection
from typing import Optional


class CatalogUpdaterPOSRepository(BaseRepository):
    def __init__(self, message_bus, configs):
        # type: (MbContextMessageBus, Configurations) -> None

        super(CatalogUpdaterPOSRepository, self).__init__(message_bus.mbcontext)

        self.message_bus = message_bus
        self.configs = configs
        self.update_type = UpdateType.catalog
        self.update_name = self.update_type.name
        self.update_value = self.update_type.value
        self.local_configs = configs.updaters[self.update_type.name]

    def get_last_downloaded_version_id(self):
        # type: () -> Optional[int]
    
        def inner_func(conn):
            # type: (Connection) -> Optional[int]
        
            query = """SELECT UpdateId
                       FROM UpdatesController
                       WHERE TypeId = '{0}' 
                        AND DownloadedDate IS NOT NULL
                        AND StatusId <> '{1}'
                       ORDER BY Id DESC
                       LIMIT 1""".format(self.update_value, UpdateStatus.error)
        
            cursor = conn.select(query)
            if not cursor.rows():
                return
        
            return int(cursor.get_row(0).get_entry("UpdateId"))
    
        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def get_last_downloaded_version_name(self):
        # type: () -> Optional[int]
    
        def inner_func(conn):
            # type: (Connection) -> Optional[int]
        
            query = """SELECT UpdateName
                       FROM UpdatesController
                       WHERE TypeId = '{}' AND AppliedDate IS NULL
                       ORDER BY Id DESC
                       LIMIT 1""".format(self.update_value)
        
            cursor = conn.select(query)
            if not cursor.rows():
                return
        
            return cursor.get_row(0).get_entry("UpdateName")
    
        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def has_pending_update_to_apply(self):
        # type: () -> Optional[CatalogUpdateData]
    
        def inner_func(conn):
            # type: (Connection) -> Optional[CatalogUpdateData]
        
            query = """SELECT  UpdateId,
                               UpdateName,
                               ObtainedDate,
                               DownloadedDate,
                               BackupDate,
                               AppliedDate,
                               NotifiedDate
                       FROM UpdatesController
                       WHERE TypeId = '{0}' AND AppliedDate IS NULL
                       ORDER BY Id DESC
                       LIMIT 1""".format(self.update_value)
        
            cursor = conn.select(query)
            row = cursor.get_row(0)
            update_data = None
        
            if row:
                update_data = CatalogUpdateData()
                update_data.update_id = row.get_entry("UpdateId")
                update_data.update_name = row.get_entry("UpdateName")
                update_data.obtained_date = row.get_entry("ObtainedDate")
                update_data.downloaded_date = row.get_entry("DownloadedDate")
                update_data.backup_date = row.get_entry("BackupDate")
                update_data.applied_date = row.get_entry("AppliedDate")
                update_data.notified_date = row.get_entry("NotifiedDate")
        
            return update_data
    
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

    def insert_new_update(self, update_id, update_name):
        # type: (str, str) -> None
    
        try:
            def inner_func(conn):
                # type: (Connection) -> None
            
                obtained_date = str(datetime.now().isoformat())
                conn.query("""INSERT OR REPLACE INTO UpdatesController
                              (UpdateId, UpdateName, TypeId, StatusId, ObtainedDate)
                              VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(update_id,
                                                                                   update_name,
                                                                                   self.update_value,
                                                                                   UpdateStatus.pending,
                                                                                   obtained_date))
        
            self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)
        except Exception as ex:
            raise ErrorInsertingNewUpdateVersion(ex)

    def skip_pending_updates(self):
        # type: () -> None
    
        try:
            def inner_func(conn):
                # type: (Connection) -> None
            
                conn.query(
                        """
                        UPDATE UpdatesController
                        SET StatusId = '{}',
                        BackupDate = DATETIME('now','localtime'),
                        AppliedDate = DATETIME('now','localtime'),
                        NotifiedDate = DATETIME('now','localtime')
                        WHERE AppliedDate IS NULL
                        """.format(UpdateStatus.skipped))
        
            self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)
        except Exception as ex:
            raise ErrorInsertingNewUpdateVersion(ex)

    def get_pending_update_to_notify(self):
        # type: () -> Optional[str]
    
        def inner_func(conn):
            # type: (Connection) -> Optional[str]
        
            query = """
                        SELECT UpdateId
                        FROM UpdatesController
                        WHERE AppliedDate IS NOT NULL AND NotifiedDate is NULL
                        ORDER BY UpdateId DESC LIMIT 1
                    """
        
            cursor = conn.select(query)
            if not cursor.rows():
                return
            
            update_id = cursor.get_row(0).get_entry("UpdateId")
            return update_id
    
        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def update_step(self, update_id, update_step):
        # type: (int, UpdateStep) -> None
    
        try:
            def inner_func(conn):
                # type: (Connection) -> None
            
                datetime_now = str(datetime.now().isoformat())
                conn.query("""UPDATE UpdatesController
                              SET '{0}' = '{1}'
                              WHERE UpdateId = '{2}' AND TypeId = '{3}'""".format(update_step,
                                                                                  datetime_now,
                                                                                  update_id,
                                                                                  self.update_value))
        
            self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)
        except Exception as ex:
            raise ErrorUpdatingStep(ex)

    def update_status(self, update_id, update_status):
        # type: (int, UpdateStatus) -> None
        try:
            def inner_func(conn):
                # type: (Connection) -> None
            
                conn.query("""UPDATE UpdatesController
                              SET StatusId = '{0}'
                              WHERE UpdateId = '{1}' AND TypeId = '{2}'""".format(update_status,
                                                                                  update_id,
                                                                                  self.update_value))
        
            self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)
        except Exception as ex:
            raise ErrorUpdatingStatus(ex)

    def restart_hv(self):
        # type: () -> None
        res = self.message_bus.mbcontext.MB_SendMessage(self.message_bus.mbcontext.hv_service, TK_HV_GLOBALRESTART)
        if res.token != msgbus.TK_SYS_ACK:
            raise ErrorRestartingHV("Could not perform HV global restart")
