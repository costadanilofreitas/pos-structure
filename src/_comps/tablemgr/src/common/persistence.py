# -*- coding: utf-8 -*-
# Module name: persistence.py
# Module Description: Python wrapper for the persistence layer
#
# Copyright © 2008 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

"""
Python wrapper for the persistence layer
Minimal usage example:
>>> import persistence
>>> driver = persistence.Driver()
>>> conn = driver.open(mbcontext) # You need a message-bus context here
>>> cursor = conn.select("SELECT * FROM mydb.MyTable")
>>> print "   |   ".join(cursor.get_names())
>>> for row in cursor:
>>>     print "|".join([str(entry) for entry in row])
>>> print "END"
"""

import ctypes
import ctypes.util
import os.path
import sys
from ctypes import c_int, c_size_t, c_void_p, c_char_p, byref, POINTER, create_string_buffer, cdll
try:
    from ctypes import windll
except:
    windll = None

_dll = None
_udll = None


def _find_library(name):
    """ finds a native library in the system, given it's name """
    platform = "win32" if sys.platform.startswith("win") else "linux" if (
        sys.platform.find("linux") != -1) else "macos"
    prefix, suffix, envvar = ({"win32": ("", ".dll", "PATH"), "linux": (
        "lib", ".so", "LD_LIBRARY_PATH"), "macos": ("lib", ".dylib", "DYLD_LIBRARY_PATH")})[platform]
    filename = "%s%s%s" % (prefix, name, suffix)
    for libpath in (os.path.join(dirname, filename) for dirname in ["./"] + os.environ.get(envvar, "").split(os.path.pathsep)):
        if os.path.exists(libpath):
            return libpath
    libpath = ctypes.util.find_library(name)
    if libpath and os.path.exists(libpath):
        return libpath
    return None


# Native APR types


_apr_status_t = c_int
_apr_size_t = c_size_t
_apr_pool_t = c_void_p
_apr_pool_tp = POINTER(_apr_pool_t)
_apr_dbd_driver_t = c_void_p
_apr_dbd_driver_tp = POINTER(_apr_dbd_driver_t)
_apr_dbd_t = c_void_p
_apr_dbd_tp = POINTER(_apr_dbd_t)
_apr_dbd_results_t = c_void_p
_apr_dbd_results_tp = POINTER(_apr_dbd_results_t)
_apr_dbd_row_t = c_void_p
_apr_dbd_row_tp = POINTER(_apr_dbd_row_t)
_apr_dbd_transaction_t = c_void_p
_apr_dbd_transaction_tp = POINTER(_apr_dbd_transaction_t)
_apr_dbd_prepared_t = c_void_p
_apr_dbd_prepared_tp = POINTER(_apr_dbd_prepared_t)

_APR_EOF_OPTIONS = (-1, 70014)
_APR_EGENERAL = 20014

# Other types

c_int_p = POINTER(c_int)
c_char_pp = POINTER(c_char_p)

#
# DLL Function definitions
#

_funcdefs = (  # For libapr-1
    ('apr_pool_create_ex', _apr_status_t, (_apr_pool_tp, _apr_pool_t, c_void_p, c_void_p,)),
    ('apr_pool_destroy', None, (_apr_pool_t,)),
    ('apr_initialize', _apr_status_t, ()),
    ('apr_pool_initialize', _apr_status_t, ()),
    ('apr_strerror', c_char_p, (_apr_status_t, c_char_p, _apr_size_t,)),
    ('apr_pool_userdata_set', _apr_status_t, (c_char_p, c_char_p, c_void_p, _apr_pool_t)),
    ('apr_pool_userdata_get', _apr_status_t, (c_char_pp, c_char_p, _apr_pool_t)),
)

_ufuncdefs = (  # For libaprutil-1
    ('apr_dbd_init', _apr_status_t, (_apr_pool_t,)),
    ('apr_dbd_get_driver', _apr_status_t, (_apr_pool_t, c_char_p, _apr_dbd_driver_tp,)),
    ('apr_dbd_open', _apr_status_t, (_apr_dbd_driver_t, _apr_pool_t, c_void_p, _apr_dbd_tp,)),
    ('apr_dbd_set_dbname', _apr_status_t, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_t, c_char_p)),
    ('apr_dbd_close', _apr_status_t, (_apr_dbd_driver_t, _apr_dbd_t,)),
    ('apr_dbd_query', c_int, (_apr_dbd_driver_t, _apr_dbd_t, c_int_p, c_char_p,)),
    ('apr_dbd_select', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_t, _apr_dbd_results_tp, c_char_p, c_int,)),
    ('apr_dbd_num_cols', c_int, (_apr_dbd_driver_t, _apr_dbd_results_t,)),
    ('apr_dbd_num_tuples', c_int, (_apr_dbd_driver_t, _apr_dbd_results_t,)),
    ('apr_dbd_get_row', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_results_t, _apr_dbd_row_tp, c_int,)),
    ('apr_dbd_get_entry', c_char_p, (_apr_dbd_driver_t, _apr_dbd_row_t, c_int,)),
    ('apr_dbd_get_name', c_char_p, (_apr_dbd_driver_t, _apr_dbd_results_t, c_int,)),
    ('apr_dbd_error', c_char_p, (_apr_dbd_driver_t, _apr_dbd_t, c_int,)),
    ('apr_dbd_escape', c_char_p, (_apr_dbd_driver_t, _apr_pool_t, c_char_p, _apr_dbd_t,)),
    ('apr_dbd_transaction_start', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_t, _apr_dbd_transaction_tp,)),
    ('apr_dbd_transaction_end', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_transaction_t,)),
    ('apr_dbd_transaction_mode_get', c_int, (_apr_dbd_driver_t, _apr_dbd_transaction_t,)),
    ('apr_dbd_transaction_mode_set', c_int, (_apr_dbd_driver_t, _apr_dbd_transaction_t, c_int)),
    ('apr_dbd_prepare', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_t, c_char_p, c_char_p, _apr_dbd_prepared_tp)),
    ('apr_dbd_pselect', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_t, _apr_dbd_results_tp, _apr_dbd_prepared_t, c_int, c_int, c_char_pp)),
    ('apr_dbd_pquery', c_int, (_apr_dbd_driver_t, _apr_pool_t, _apr_dbd_t, c_int_p, _apr_dbd_prepared_t, c_int, c_char_pp)),
)

#
# Private functions
#


def _aprcall_err(fname, errfunc, *args):
    global _dll, _udll
    func = getattr(_udll, fname, False) or getattr(_dll, fname)
    status = func(*args)
    if status != 0:
        raise AprDbdException(errfunc(status), status)


def _aprcall(fname, *args):
    global _dll, _udll
    """Calls an apr function that returns a status code and raises an error if the status is non-zero"""
    func = getattr(_udll, fname, False) or getattr(_dll, fname)
    status = func(*args)
    if status != 0:
        raise AprException("Error on function '%s'" % (fname), status)


def _apr_strerror(statcode):
    global _dll
    """Call apr_strerror to retrieve a human-readable message for an error code"""
    buf = create_string_buffer("", 512)
    return _dll.apr_strerror(statcode, buf, 512)


def _pool_create():
    """Creates an APR memory pool"""
    pool = _apr_pool_t(0)
    _aprcall('apr_pool_create_ex', byref(pool), None, None, None)
    return pool


def _pool_destroy(pool):
    global _dll
    """Destroys an APR memory pool"""
    _dll.apr_pool_destroy(pool)


def _params_to_charpp(params):
    """Converts a dictionary of parameters into a (char **) array"""
    if not params:
        params = {}
    # ctypes array types are constructed by multiplying a type by the number
    # of elements
    array_type = (c_char_p * (len(params) + 1))
    array = array_type()
    index = 0
    for name, value in params.iteritems():
        if value is None:
            value = "null"
        array[index] = ("%s=%s" % (name, value)).encode("UTF-8")
        index += 1
    return array


def _load_native():
    """ loads native libraries """
    global _load_native, _udll, _dll
    dllLoader = windll if (sys.platform[:3] == 'win') else cdll
    # libaprutil-1 (I don't know exactly why, but on MacOS X we must load "aprutil" BEFORE "apr"
    # otherwise it will fail to locate a symbol)
    _libpath = _find_library("aprutil-1") or _find_library("libaprutil-1")
    if not _libpath:
        raise ImportError("Could not find library 'libaprutil-1'.")
    _udll = dllLoader.LoadLibrary(_libpath)

    # libapr-1
    _libpath = _find_library("apr-1") or _find_library("libapr-1")
    if not _libpath:
        raise ImportError("Could not find library 'libapr-1'.")
    _dll = dllLoader.LoadLibrary(_libpath)
    _load_native = None


def _init_dll():
    """
    Perform the DLL initialization inside a function, to avoid
    leaving variables in the module scope
    """
    global _init_dll, _dll, _udll
    if _load_native:
        _load_native()
    defs = (('libaprutil-1', _udll, _ufuncdefs), ('libapr-1', _dll, _funcdefs))
    for libname, dll, funcdefs in defs:
        for name, restype, argtypes in funcdefs:
            func = getattr(dll, name, None)
            if func is None:
                raise ImportError(
                    "Could not find function '%s' on '%s' library." % (name, libname))
            func.restype = restype
            func.argtypes = argtypes
    # Call initialization functions
    _aprcall('apr_initialize')
    _aprcall('apr_pool_initialize')
    _aprcall('apr_dbd_init', _pool_create())
    _init_dll = None


#
# Public APIs
#


__all__ = ('Driver', 'Connection', 'Cursor', 'Row', 'DbdException', 'AprException', 'AprDbdException',
           'APR_DBD_TRANSACTION_COMMIT', 'APR_DBD_TRANSACTION_ROLLBACK', 'APR_DBD_TRANSACTION_IGNORE_ERRORS',)

APR_DBD_TRANSACTION_COMMIT = 0x00  # commit the transaction
APR_DBD_TRANSACTION_ROLLBACK = 0x01  # rollback the transaction
APR_DBD_TRANSACTION_IGNORE_ERRORS = 0x02  # ignore transaction errors


class Driver(object):

    """ class Driver(object)
    This is the class that should be instantiated to use the persistence module.
    Instances of this class encapsulates an "apr dbd driver".
    """

    def __init__(self, name="persistcomp"):
        """ Driver(name="persistcomp") -> instance
        Creates a new persistence driver
        @raise AprException on any APR error
        """
        if _init_dll:
            _init_dll()
        self._pool = _pool_create()
        self._driver = _apr_dbd_driver_t()
        _aprcall('apr_dbd_get_driver', self._pool, name, byref(self._driver))

    def __del__(self):
        """private - object destructor that releases the native instance"""
        if _pool_destroy:  # This will be None if the module has already been unloaded
            _pool_destroy(self._pool)

    def open(self, mbcontext, dbname=None, service_name=None, logger=None):
        """ obj.open(self, mbcontext) -> Connection
        Opens a new database connection.
        @param mbcontext: {msgbus.MBContext} - Message-bus context to use, or {str} (string connection)
        @param dbname: {str} - Optional dbname to set right after opening the connection (the same as calling "set_dbname")
        @param service_name: {str} - Optional persistence service name to connect to
        @return {Connection} - the connection instance
        @raise AprException on any APR error
        """
        if hasattr(mbcontext, '_pctx'):
            conn_string = mbcontext._pctx
            mbctxt = mbcontext
        else:
            conn_string = str(mbcontext)
            mbctxt = None
        return Connection(conn_string, self, dbname, service_name, mbctxt, logger)


class Connection(object):

    """ class Connection(object)
    Represents a database connection.
    This class is instantiated by #Driver.open
    """
    _open = False   # Indicates if this connection is open

    def __init__(self, conn_string, driverobj, dbname=None, service_name=None, mbcontext=None, logger=None):
        """private - Connection constructor"""
        self._driverobj = driverobj  # This avoids the driver being unloaded while the connection is active
        self._driver = driverobj._driver
        self._pool = _pool_create()
        self._handle = _apr_dbd_t()
        self._trans = None
        self._service_name = service_name
        self._number_of_instances = -1
        self._instaces = []
        self.logger = logger
        if self._service_name:
            _aprcall('apr_pool_userdata_set', self._service_name,
                     "PERSISTENCE_SERVICE", None, self._pool)
        _aprcall('apr_dbd_open', self._driver, self._pool,
                 conn_string, byref(self._handle))
        self._open = True
        if dbname and self.is_multi_instance():
            self.set_dbname(dbname)
        if mbcontext is not None:
            from os import environ
            from msgbus import MBService, TK_PERSIST_GETINSTNBR, TK_PERSIST_INITINPROGRESS, FM_PARAM, TK_SYS_ACK
            while True:
                msg = mbcontext.MB_SendMessage(mbcontext.MB_LocateService(MBService(environ["HVIP"], int(environ["HVPORT"])), (service_name or "Persistence")), TK_PERSIST_GETINSTNBR, FM_PARAM, "", -1)
                if msg.token == TK_PERSIST_INITINPROGRESS:
                    from time import sleep
                    sleep(1)
                    continue
                elif msg.token == TK_SYS_ACK:
                    params = msg.data.split("\0")
                    if len(params) > 0:
                        self._number_of_instances = int(params[0])
                    if len(params) > 1:
                        self._instaces = [int(p) for p in params[1:]]
                break

        self.log("Opening connection: %s", self._handle)

    def __del__(self):
        """private - object destructor that releases the native instance"""
        if _pool_destroy:  # This will be None if the module has already been unloaded
            self.close()

    def _error_message(self, errnum):
        """private - retrieves an error message using 'apr_dbd_error' """
        global _udll
        return _udll.apr_dbd_error(self._driver, self._handle, errnum)

    def close(self):
        """ obj.close()
        Closes this connection (it cannot be used anymore after this).
        @raise AprException on any APR error
        """
        if self._open:
            self.log("Closing connection: %s", self._handle)
            if self._trans:
                self.log("Connection was executing a transaction: %s", self._handle)
                self.transaction_end()
            _aprcall('apr_dbd_close', self._driver, self._handle)
            _pool_destroy(self._pool)
            self._open = False
            del self._driverobj
        else:
            self.log("Connection was already closed: %s", self._handle)

    def get_number_of_instances(self):
        """ obj.get_number_of_instances() -> int
        Retrieves the number of databases instances available in the Persistence component is applicable
        @return Number of instances in the connected persistence component
        """
        return self._number_of_instances

    def get_instances(self):
        """ obj.get_instances() -> int[]
        Retrieves the instance ids list to be used in the set_dbname call.
        @return List of int with valid instance ids
        """
        return self._instaces

    def is_multi_instance(self):
        """ obj.is_multi_instance() -> bool
        Checks the current working mode of the persistence component.
        @return True if the current working mode is multi-instance, othwerwise False.
        """
        global _udll
        if not self._open:
            raise DbdException("Connection already closed")
        status = _udll.apr_dbd_set_dbname(
            self._driver, self._pool, self._handle, None)
        return (status != _APR_EGENERAL)

    def set_dbname(self, dbname):
        """ obj.set_dbname(dbname)
        @param dbname The database instance which the user desires to work.
        @raise AprException if an invalid instance was passed in the dbname parameter.
        """
        if not self._open:
            raise DbdException("Connection already closed")
        _aprcall('apr_dbd_set_dbname', self._driver,
                 self._pool, self._handle, dbname)

    def query(self, sql):
        """ obj.query(sql) -> int
        Executes a SQL statement and returns the number of rows affected.
        @param sql: {str} - sql statement. multiple statements are allowed by separating
                    them with '\0' characters. The last (or single) statement should be
                    terminated with a '\0', but that is optional since this method ensures
                    this (if you need better performance, add it yourself)
        @return {int} - the number of rows affected
        @raise AprException on any APR error
        @raise DbdException if this connection is closed
        """
        if not self._open:
            raise DbdException("Connection already closed")
        self.log("Executing query: %s - %s", self._handle, sql)
        nrows = c_int(0)
        if not sql.endswith("\0"):
                # The sql buffer MUST end with two '\0' (one is already added
                # by ctypes, but we better ensure)
            sql += "\0\0"
        _aprcall_err('apr_dbd_query', self._error_message,
                     self._driver, self._handle, byref(nrows), sql)
        self.log("Executed query: %s - %s", self._handle, sql)
        return nrows.value

    def pquery(self, procname, **kargs):
        """ obj.pquery(procname, **kargs) -> int
        Executes a prepared procedure and returns the number of affected rows
        @param procname: {str} - the prepared procedure name
        @param kargs: each keyword argument is a procedure parameter
        @return {int} - the number of rows affected
        @raise AprException on any APR error
        @raise DbdException if this connection is closed
        """
        if not self._open:
            raise DbdException("Connection already closed")
        self.log("Executing pquery: %s - %s", self._handle, procname)
        nrows = c_int(0)
        pool = _pool_create()
        try:
            procedure = _apr_dbd_prepared_t()
            # Prepare the procedure
            _aprcall_err('apr_dbd_prepare', self._error_message,
                         self._driver, pool, self._handle, "", procname, byref(procedure))
            # Build the list of parameters
            array = _params_to_charpp(kargs)
            self.log("Parameters pquery: %s - %s - %s", self._handle, procname, ','.join('{0}={1!r}'.format(k, v) for k, v in kargs.items()))
            _aprcall_err('apr_dbd_pquery', self._error_message, self._driver,
                         pool, self._handle, byref(nrows), procedure, len(kargs), array)
        finally:
            _pool_destroy(pool)
        self.log("Executed pquery: %s - %s", self._handle, procname)
        return nrows.value

    def select(self, sql):
        """ obj.select(sql) -> Cursor
        Executes a SQL "select" query and returns a cursor to the results
        @param sql: {str} - sql statement
        @return {Cursor} - a cursor with the query results
        @raise AprException on any APR error
        @raise DbdException if this connection is closed
        """
        if not self._open:
            raise DbdException("Connection already closed")
        self.log("Executing select: %s - %s", self._handle, sql)
        ret = Cursor(self, sql)
        self.log("Executed select: %s - %s", self._handle, sql)
        return ret

    def pselect(self, procname, **kargs):
        """ obj.pselect(procname, **kargs) -> Cursor
        Executes a prepared procedure query and returns a cursor to the results
        @param procname: {str} - the prepared procedure name
        @param kargs: each keyword argument is a procedure parameter
        @return {ProcedureCursor} - a cursor with the query results
        @raise AprException on any APR error
        @raise DbdException if this connection is closed
        """
        if not self._open:
            raise DbdException("Connection already closed")
        self.log("Executing pselect: %s - %s", self._handle, procname)
        ret = ProcedureCursor(self, procname, kargs)
        self.log("Executed pselect: %s - %s", self._handle, procname)
        return ret

    def escape(self, string):
        """obj.escape(string) -> str
        Escapes a string to be inserted into an SQL estatement.
        @param string: {str} - the string to be escaped
        @return {str} - the escaped string
        """
        global _udll
        if isinstance(string, unicode):
            string = string.encode("UTF-8")
        return _udll.apr_dbd_escape(self._driver, self._pool, string, self._handle)

    def transaction_start(self):
        """obj.transaction_start()
        Starts a transaction in the database
        @raise AprException on any APR error
        @raise DbdException if this connection is closed
        """
        if not self._open:
            raise DbdException("Connection already closed")
        if self._trans:
            self.log("Already in a transaction")
            return
        self.log("Starting a transaction: %s", self._handle)
        trans = _apr_dbd_transaction_t()
        _aprcall_err('apr_dbd_transaction_start', self._error_message,
                     self._driver, self._pool, self._handle, byref(trans))
        self._trans = trans

    def transaction_end(self):
        """obj.transaction_end()
        Closes the currently open transaction in the database
        @raise AprException on any APR error
        @raise DbdException if this connection is closed
        """
        if not self._open:
            raise DbdException("Connection already closed")
        if not self._trans:
            self.log("Was not in a transaction")
            return
        self.log("Ending a transaction: %s", self._handle)
        _aprcall_err('apr_dbd_transaction_end', self._error_message,
                     self._driver, self._pool, self._trans)
        self._trans = None

    def transaction_mode_get(self):
        """obj.transaction_mode_get()
        Retrieves the current transaction mode (APR_DBD_TRANSACTION_COMMIT,
        APR_DBD_TRANSACTION_ROLLBACK or APR_DBD_TRANSACTION_IGNORE_ERRORS)
        @raise DbdException if this connection is closed
        """
        global _udll
        if not self._open:
            raise DbdException("Connection already closed")
        if not self._trans:
            return
        return _udll.apr_dbd_transaction_mode_get(self._driver, self._trans)

    def transaction_mode_set(self, mode):
        """obj.transaction_mode_get()
        Sets the current transaction mode
        @param mode: {int} - APR_DBD_TRANSACTION_COMMIT, APR_DBD_TRANSACTION_ROLLBACK or APR_DBD_TRANSACTION_IGNORE_ERRORS
        @raise DbdException if this connection is closed
        """
        global _udll
        if not self._open:
            raise DbdException("Connection already closed")
        if not self._trans:
            return
        _udll.apr_dbd_transaction_mode_set(
            self._driver, self._trans, int(mode))

    def log(self, msg, *params):
        if self.logger is not None:
            self.logger.debug(msg, *params)


class Cursor(object):

    """ class Cursor(object)
    Cursor that holds a result set for a SQL query.
    This class is instantiated by #Connection.select
    """

    def __init__(self, connobj, sql):
        """private - Cursor constructor"""
        global _udll
        self._connobj = connobj  # This avoids the connection being unloaded while the cursor is active
        self._driver = connobj._driver
        self._handle = connobj._handle
        self._pool = _pool_create()
        self._res = _apr_dbd_results_t()
        _aprcall_err('apr_dbd_select', connobj._error_message,
                     self._driver, self._pool, self._handle, byref(self._res), sql, 0)
        self._maxcols = _udll.apr_dbd_num_cols(self._driver, self._res)
        self._colnames = []
        self._coltypes = []
        for i in xrange(self._maxcols):
            self._colnames.append(self.get_name(i))
            value = c_char_p()
            _aprcall('apr_pool_userdata_get', byref(value), "COLTYPE", self._pool)
            self._coltypes.append(value.value)

    def __del__(self):
        """private - object destructor that releases the native instance"""
        if _pool_destroy:  # This will be None if the module has already been unloaded
            _pool_destroy(self._pool)
        del self._connobj

    def __iter__(self):
        """creates an iterator for the rows of this cursor"""
        return _RowsIterator(self)

    def cols(self):
        """ obj.cols() -> int
        Retrieves the total number of columns on this cursor
        @return {int} - number of columns
        """
        return self._maxcols

    def rows(self):
        """ obj.rows() -> int
        Retrieves the total number of rows on this cursor
        @return {int} - number of rows
        """
        global _udll
        return _udll.apr_dbd_num_tuples(self._driver, self._res)

    def get_name(self, col):
        """ obj.get_name(col) -> str
        Retrieves the name of a column
        @param col: {int} - index of the column (zero-based)
        @return {str} - Name of the column, or None if it does not exist
        """
        global _udll
        return _udll.apr_dbd_get_name(self._driver, self._res, col)

    def get_type(self, col):
        """ obj.get_name(col) -> str
        Retrieves the name of a column
        @param col: {int} - index of the column (zero-based)
        @return {str} - Type of column description
        """
        return self._coltypes[col] if col < len(self._coltypes) else "SQL_UNKNOWN"

    def get_names(self):
        """ obj.get_names() -> list
        Retrieves the name of all columns
        @return {tuple} - Tuple of column names
        """
        return tuple(self._colnames)

    def get_row(self, rownum):
        """ obj.get_row() -> Row
        Retrieves a single row of this cursor
        @param rownum: {int} - index of the row (zero-based)
        @return {Row} - the Row instance, or None if that row does not exist
        """
        try:
            return Row(self, rownum)
        except AprException, ex:
            if ex.errorcode in _APR_EOF_OPTIONS:  # No such row
                return None
            raise


class ProcedureCursor(Cursor):

    """ class ProcedureCursor(Cursor)
    Cursor that holds a result set for a procedure query.
    This class is instantiated by #Connection.pselect
    """

    def __init__(self, connobj, procname, params):
        """private - Cursor constructor"""
        global _udll
        self._connobj = connobj  # This avoids the connection being unloaded while the cursor is active
        self._driver = connobj._driver
        self._handle = connobj._handle
        self._pool = _pool_create()
        self._res = _apr_dbd_results_t()
        procedure = _apr_dbd_prepared_t()
        # Prepare the procedure
        _aprcall_err('apr_dbd_prepare', connobj._error_message, self._driver,
                     self._pool, self._handle, "", procname, byref(procedure))
        # Build the list of parameters
        array = _params_to_charpp(params)
        _aprcall_err('apr_dbd_pselect', connobj._error_message, self._driver,
                     self._pool, self._handle, byref(self._res), procedure, 0, len(params), array)
        self._maxcols = _udll.apr_dbd_num_cols(self._driver, self._res)
        self._colnames = []
        self._coltypes = []
        for i in xrange(self._maxcols):
            self._colnames.append(self.get_name(i))
            value = c_char_p()
            _aprcall('apr_pool_userdata_get', byref(value), "COLTYPE", self._pool)
            self._coltypes.append(value.value)

    def get_output(self, name):
        value = c_char_p()
        _aprcall('apr_pool_userdata_get', byref(value), name, self._pool)
        result = None
        try:
            result = value.value
        except:
            pass
        return result


class Row(object):

    """ class Row(object)
    Represents a row in a cursor.
    This class is instantiated by #Cursor.get_row, or by iterating on a Cursor instance
    """

    def __init__(self, cursorobj, rownum):
        """private - Row constructor"""
        self._cursorobj = cursorobj  # This avoids the cursor being unloaded while the row is active
        self._res = cursorobj._res
        self._pool = cursorobj._pool
        self._driver = cursorobj._driver
        self._row = _apr_dbd_row_t()
        _aprcall('apr_dbd_get_row', self._driver, self._pool,
                 self._res, byref(self._row), rownum)

    def __iter__(self):
        """creates an iterator for the entries of this row"""
        return _EntriesIterator(self, self._cursorobj.cols())

    def get_entry(self, col):
        """ obj.get_entry(col) -> str
        Retrieves a single entry of this row.
        @param col: {int} - column index of the entry (zero-based), or
                    {str} - column name of the entry
        @return {str} - the row entry, or None if it is NULL on the database
        """
        global _udll
        if isinstance(col, str):
            col = self._cursorobj._colnames.index(col)
        return _udll.apr_dbd_get_entry(self._driver, self._row, col)


class _RowsIterator(object):

    """private - rows iterator"""

    def __init__(self, cursor):
        self.idx = 0
        self.cur = cursor

    def __iter__(self):
        return self

    def next(self):
        val = self.cur.get_row(self.idx)
        if val is None:
            raise StopIteration
        self.idx += 1
        return val


class _EntriesIterator(object):

    """private - entries iterator"""

    def __init__(self, row, maxcols):
        self.idx = 0
        self.row = row
        self.max = maxcols

    def __iter__(self):
        return self

    def next(self):
        if self.idx >= self.max:
            raise StopIteration
        val = self.row.get_entry(self.idx)
        self.idx += 1
        return val


class DbdException(Exception):

    """Base exception for this module (all other exceptions descend from this)"""
    pass


class AprException(DbdException):

    """Exception raised for APR errors"""

    def __init__(self, message, errorcode):
        message += (". Status: (%d). APR Message: %s" %
                    (errorcode, _apr_strerror(errorcode)))
        self.errorcode = errorcode
        DbdException.__init__(self, message)


class AprDbdException(AprException):

    """Exception raised for APR-DBD errors"""

    def __init__(self, message, errorcode):
        self.errorcode = errorcode
        DbdException.__init__(self, message)
