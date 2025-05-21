import persistence
from msgbus import MBEasyContext
from pos_model import PosConnection


class BaseRepository(object):
    def __init__(self, mbcontext, dbname = None):
        # type: (MBEasyContext, str) -> None
        self.mbcontext = mbcontext
        self.dbname = dbname
        self.conn = None  # type: persistence.Connection

    def __enter__(self):
        self.conn = persistence.Driver().open(self.mbcontext)
        if self.dbname is not None:
            self.conn.set_dbname(self.dbname)

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.conn is not None:
            self.conn.close()


class BaseTransactionRepository(BaseRepository):
    def __init__(self, mbcontext, dbname = None):
        # type: (MBEasyContext, str) -> None
        super(BaseTransactionRepository, self).__init__(mbcontext, dbname)

    def __enter__(self):
        self.open_connection()
        self.begin_transaction()

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value is None:
            self.commit()
        else:
            self.rollback()

        self.close_connection()

    def open_connection(self):
        self.conn = persistence.Driver().open(self.mbcontext)
        if self.dbname is not None:
            self.conn.set_dbname(self.dbname)

    def begin_transaction(self):
        if self.conn:
            self.conn.transaction_start()
            self.conn.query("BEGIN TRANSACTION")

    def commit(self):
        if self.conn:
            self.conn.query("COMMIT")
            self.conn.transaction_end()

    def rollback(self):
        if self.conn:
            self.conn.query("ROLLBACK")
            self.conn.transaction_end()

    def close_connection(self):
        if self.conn:
            self.conn.close()


class BasePosRepository(object):
    def __init__(self, mbcontext, pos_list):
        # type: (MBEasyContext, list) -> None
        self.mbcontext = mbcontext
        self.pos_list = pos_list
        self.pos_connection_list = []
        self.pos_connection_disct = {}

    def __enter__(self):
        self.open_all_connections()

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close_all_connections()

    def open_all_connections(self):
        for pos_id in self.pos_list:
            pos_connection = persistence.Driver().open(self.mbcontext, dbname=str(pos_id))
            self.pos_connection_list.append(PosConnection(pos_id, pos_connection))
            self.pos_connection_disct[pos_id] = pos_connection

    def close_all_connections(self):
        for pos_connection in self.pos_connection_list:  # type: persistence.Connection
            pos_connection.close()


class BasePosTransactionRepository(BasePosRepository):
    def __init__(self, mbcontext, pos_list):
        super(BasePosTransactionRepository, self).__init__(mbcontext, pos_list)

    def __enter__(self):
        super(BasePosTransactionRepository, self).__enter__()

        self.begin_transaction_on_all_coonections()

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value:
            self.rollback_on_all_connection()
        else:
            self.commit_on_all_connections()

        super(BasePosTransactionRepository, self).__exit__(exception_type, exception_value, exception_traceback)

    def begin_transaction_on_all_coonections(self):
        for pos_connection in self.pos_connection_list:  # type: PosConnection
            pos_connection.transaction_start()
            pos_connection.query("BEGIN TRANSACTION")

    def commit_on_all_connections(self):
        for pos_connection in self.pos_connection_list:  # type: persistence.Connection
            pos_connection.query("COMMIT")
            pos_connection.transaction_end()

    def rollback_on_all_connection(self):
        for pos_connection in self.pos_connection_list:  # type: persistence.Connection
            pos_connection.query("ROLLBACK")
            pos_connection.transaction_end()
