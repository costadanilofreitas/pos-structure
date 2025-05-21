from datetime import datetime

from application.model import UpdateType, UserUpdateData, UpdateStatus
from application.model.configuration import Configurations
from application.model.customexception import ErrorInsertingNewUpdateVersion
from mbcontextmessagehandler import MbContextMessageBus
from mwhelper import BaseRepository
from persistence import Connection
from typing import Dict


class UserUpdaterPOSRepository(BaseRepository):

    def __init__(self, message_bus, configs):
        # type: (MbContextMessageBus, Configurations) -> None

        super(UserUpdaterPOSRepository, self).__init__(message_bus.mbcontext)

        self.message_bus = message_bus
        self.configs = configs
        self.update_type = UpdateType.user
        self.update_value = self.update_type.value
        self.local_configs = configs.updaters[self.update_type.name]

    def update_users(self, users_update_data):
        # type: (Dict[int, UserUpdateData]) -> Dict[str: str]
    
        def inner_func(conn):
            # type: (Connection) -> None

            for user in users_update_data:
                user = users_update_data[user]
                
                if user.end_date is None:
                    user.end_date = "NULL"
                else:
                    user.end_date = "'{}'".format(user.end_date)
                    
                cursor = conn.select("SELECT 1 from Users WHERE UserId={}".format(user.user_id))
                user_already_exists = cursor.rows() > 0
                if user_already_exists:
                    conn.query("""UPDATE Users
                                    SET LongName='{}',
                                        Password='{}',
                                        Level={},
                                        Status={},
                                        AdmissionDate='{}',
                                        TerminationDate={},
                                        PayRate={}
                                    WHERE UserId={}"""
                               .format(conn.escape(user.long_name),
                                       user.password,
                                       user.level,
                                       user.status,
                                       user.start_date,
                                       user.end_date,
                                       user.pay_rate,
                                       user.user_id))
                else:
                    query = """INSERT INTO Users(UserId,
                                               UserName,
                                               LongName,
                                               Password,
                                               Level,
                                               Status,
                                               AdmissionDate,
                                               TerminationDate,
                                               PayRate)
                               VALUES ({0}, '{0}', '{1}', '{2}', {3}, {4}, '{5}', {6}, {7})""" \
                        .format(user.user_id,
                                conn.escape(user.long_name),
                                user.password,
                                user.level,
                                user.status,
                                user.start_date,
                                user.end_date,
                                user.pay_rate)
                    
                    conn.query(query)
    
        self.execute_with_transaction(inner_func)

    def insert_new_user_update(self, update_id, update_name):
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

    def get_last_user_update_id(self):
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
