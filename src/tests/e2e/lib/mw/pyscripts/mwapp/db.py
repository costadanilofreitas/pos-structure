# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\db.py
import json
from functools import wraps

class ResultProxy(object):
    """ ResultProxy(cursor) -> ResultProxy
    
        This is a helper class that wraps a DBD Driver Cursor object
        and provides easier access to columns names and row data
    
        @param cursor: {DBDriver} - DB Driver Cursor object
        @return: ResultProxy instance.
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def columns(self):
        """ columns()
        
            This method returns a list of the column names contained
            in the provided query result.
        
            @return: [str].
        """
        return [ self.cursor.get_name(i) for i in xrange(self.cursor.cols()) ]

    def fetchall(self):
        """ fetchall()
        
            This method returns a list column/value dicts
            representing the rows in the cursor.
        
            @return: [{column_name: value}].
        """
        result = []
        for row in self.cursor:
            result.append(dict([ (self.cursor.get_name(i), row.get_entry(i)) for i in xrange(self.cursor.cols()) ]))

        return result

    def first(self):
        """ first()
        
            This method returns a column/value dict
            representing the first row in the cursor.
        
            @return: {column_name: value}.
        """
        for row in self.cursor:
            result = dict([ (self.cursor.get_name(i), row.get_entry(i)) for i in xrange(self.cursor.cols()) ])
            break
        else:
            result = None

        return result


class DBConnection(object):
    """ DBConnection(db_driver, mbcontext, service_name) -> DBConnection
    
        This is a helper class that wraps a DB Driver Connection object
        and provides easier access to commonly used functions and wraps
        query results in a ResultProxy.
    
        @param db_driver: {Driver} - DB Driver object
        @param mbcontext: {MBContext} - message bus context object
        @param service_name: {str} - Name of database component
        @return: DBConnection instance.
    """

    def __init__(self, db_driver, mbcontext, service_name):
        self.dbd_conn = db_driver.open(mbcontext, service_name=service_name)
        self.connected = True
        self.transacting = False

    def __del__(self):
        self.close()

    def close(self):
        if self.connected:
            self.dbd_conn.close()
            self.connected = False

    def transaction_decorate(func):
        """ This decorator function will wrap SQL function calls in a transaction.
        
        If utilizing a start/rollback/commit pattern, you should run execute a start_transaction before
        calling your pselect or pquery procedure, and an end_transaction after.
        
        This will cause this decorator function to see that the call is already transacting,
        and it will not attempt to wrap the call.
        """

        @wraps(func)
        def func_wrapper(self, *args, **kwargs):
            if self.transacting:
                return func(self, *args, **kwargs)
            self.start_transaction()
            try:
                return func(self, *args, **kwargs)
            except:
                raise
            finally:
                self.end_transaction()

        return func_wrapper

    @transaction_decorate
    def pselect(self, name, **params):
        cursor = self.dbd_conn.pselect(name, **params)
        return ResultProxy(cursor)

    @transaction_decorate
    def pquery(self, name, **params):
        cursor = self.dbd_conn.pquery(name, **params)
        return ResultProxy(cursor)

    def select(self, statement):
        cursor = self.dbd_conn.select(statement)
        return ResultProxy(cursor)

    def query(self, statement):
        cursor = self.dbd_conn.query(statement)
        return ResultProxy(cursor)

    def begin(self):
        """ begin()
        
            Wrapper function to start a database transaction on a given connection.
        """
        self.dbd_conn.query('BEGIN TRANSACTION;\x00\x00')

    def commit(self):
        """ commit()
        
            Wrapper function to commit a database transaction on a given connection.
        """
        self.dbd_conn.query('COMMIT TRANSACTION;\x00\x00')

    def rollback(self):
        """ rollback()
        
            Wrapper function to rollback a database transaction on a given connection.
        """
        self.dbd_conn.query('ROLLBACK TRANSACTION;\x00\x00')

    def start_transaction(self):
        self.dbd_conn.transaction_start()
        self.transacting = True

    def end_transaction(self):
        if self.transacting:
            self.dbd_conn.transaction_end()
            self.transacting = False


def objects_to_pgtextarray(obj, keys):
    """ objects_to_pgtextarray(obj, keys)
    
        Given a list of "objects"(dicts), convert the data into a Postgres
        consumable text array.
    
        @param obj: {[dicts]} - List of dictionaries based on database tables
        @param keys: {[str]} - List of key names to be converted
        @return {str} - Postgres consumable text array string
    """

    def to_str(value):
        if isinstance(value, (list, dict)):
            value = json.dumps(value).replace('"', '\\\\\\"')
        else:
            value = unicode(value).replace('"', '')
        return value

    res = [ map(r.get, keys) for r in obj ]
    text = '{%s}' % ','.join([ '"{%s}"' % ','.join([ ('\\"%s\\"' % to_str(f) if f is not None else 'NULL') for f in row ]) for row in res ])
    return text


def object_to_pgtextarray(obj, keys, escape = False):
    """ object_to_pgtextarray(obj, keys, escape=False)
    
        Given an object (dict), convert the data into a Postgres
        consumable text array.
    
        @param obj: {[dicts]} - Dictionary based object
        @param keys: {[str]} - List of key names to be converted
        @param escape: {bool} - Flag to control if quotes are escaped
        @return {str} - Postgres consumable text array string
    """

    def to_str(value):
        if isinstance(value, (list, dict)):
            value = json.dumps(value).replace('"', '\\\\\\"')
        else:
            value = unicode(value).replace('"', '')
        return value

    res = map(obj.get, keys)
    if escape:
        text = '"{%s}"' % ','.join([ ('\\"%s\\"' % to_str(f) if f is not None else 'NULL') for f in res ])
    else:
        text = '{%s}' % ','.join([ ('"%s"' % to_str(f) if f is not None else 'NULL') for f in res ])
    return text