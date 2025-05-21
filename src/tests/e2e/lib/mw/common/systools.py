# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\wrappers\python\systools.py
import sys
import os
import threading
import traceback
import ctypes
import ctypes.util
from datetime import datetime
from cStringIO import StringIO
from ctypes import c_char_p, c_int32, cdll, create_string_buffer
try:
    from ctypes import windll
except:
    windll = None

import pickle
from contextlib import contextmanager
from time import time
__all__ = ('sys_log', 'sys_log_trace', 'sys_log_debug', 'sys_log_info', 'sys_log_warning', 'sys_log_error', 'sys_log_fatal', 'sys_log_exception', 'sys_parsefilepath', 'sys_errget', 'sys_errset')
__pid = os.getpid()
__compname = os.environ.get('HVCOMPNAME') or 'unknown'

def _find_library(name):
    """ finds a native library in the system, given it's name """
    platform = 'win32' if sys.platform.startswith('win') else ('linux' if sys.platform.find('linux') != -1 else 'macos')
    prefix, suffix, envvar = {'win32': ('', '.dll', 'PATH'),
     'linux': ('lib', '.so', 'LD_LIBRARY_PATH'),
     'macos': ('lib', '.dylib', 'DYLD_LIBRARY_PATH')}[platform]
    filename = '%s%s%s' % (prefix, name, suffix)
    for libpath in (os.path.join(dirname, filename) for dirname in ['./'] + os.environ.get(envvar, '').split(os.path.pathsep)):
        if os.path.exists(libpath):
            return libpath

    libpath = ctypes.util.find_library(name)
    if libpath and os.path.exists(libpath):
        return libpath
    else:
        return None


def sys_log(level, message):
    strtime = datetime.now().isoformat()[:23]
    if len(strtime) == 19:
        strtime += '.000'
    threadid = threading.currentThread().ident or 0
    file, line, func, text = __caller(1)
    file = file[max(file.rfind('\\'), file.rfind('/')) + 1:]
    try:
        str_msg = str(message)
    except UnicodeEncodeError:
        str_msg = str(message.encode('utf-8'))

    for logline in str_msg.splitlines():
        print '<%s> %s - %s; [%s - %s - %s:%d (%d:0x%X)]' % (level,
         strtime,
         logline,
         __compname,
         func,
         file,
         line,
         __pid,
         threadid)

    try:
        sys.stdout.flush()
    except IOError:
        pass


def sys_log_trace(message):
    sys_log('TRACE', message)


def sys_log_debug(message):
    sys_log('DEBUG', message)


def sys_log_info(message):
    sys_log('INFO ', message)


def sys_log_warning(message):
    sys_log('WARN ', message)


def sys_log_error(message):
    sys_log('ERROR', message)


def sys_log_fatal(message):
    sys_log('FATAL', message)


def sys_log_exception(message, level = 'ERROR'):
    buf = StringIO()
    traceback.print_exc(file=buf)
    buf = buf.getvalue()
    if isinstance(buf, unicode):
        buf = buf.encode('UTF-8')
    if isinstance(message, unicode):
        message = message.encode('UTF-8')
    sys_log(level, '%s\n%s' % (message, buf))


def sys_parsefilepath(path):
    """ sys_parsefilepath(path) -> str
    Parses a file path, replacing environment variables inside braces: '{ENV}'
    @param path: {str} - File path with optional environment variable. E.g.: "{MY_PATH}/subfolder"
    @return {str} - the file path with the environment variable replaced. E.g.: "/tmp/subfolder"
    """
    start, end = path.find('{'), path.find('}')
    if start != -1 and end != -1 and end > start + 1:
        envvar = os.environ.get(path[start + 1:end])
        if envvar is not None:
            return path[:start] + envvar + path[end + 1:]
    return path


def sys_errget(code):
    """
    sys_errget(code) -> the error description for the given error code
    
    @brief - retrieve the error description for the given error code
    
    @param - sysErrors code - code to retrieve the message
    @return the error description for the given error code
    """
    try:
        return Syslib().errget(code)
    except:
        return '(could not get error message)'


def sys_errset(code, msg):
    """
    sys_errset(code,msg) -> SE_SUCCESS for success setting the message or SE_NOTFOUND if the given code wasn't found
    
    @brief - sets a new error message for an existent error code
    
    @param - sysErrors code - error code to set the message
    @param - const char *message - message to set (this message must remain allocated in the caller memory stack)
    @return - SE_SUCCESS for success setting the message or SE_NOTFOUND if the given code wasn't found
    """
    return Syslib().errset(code, msg)


class Syslib(object):
    _dll__spam = None
    _dynmsgs__spam = list()
    _funcdefs__spam = (('sys_errget', c_char_p, (c_int32,)), ('sys_errset', c_int32, (c_int32, c_char_p)))

    def __init__(self):
        """ starts the systools.dll library  """
        if self._dll__spam:
            return
        else:
            _libpath = _find_library('systools')
            if not _libpath:
                raise ImportError("Could not find library 'systools'.")
            dllLoader = windll if sys.platform[:3] == 'win' else cdll
            self._dll__spam = dllLoader.LoadLibrary(_libpath)
            for name, restype, argtypes in self._funcdefs__spam:
                func = getattr(self._dll__spam, name, None)
                if func is None:
                    raise ImportError("Could not find function '%s' on 'systools' library." % name)
                func.restype = restype
                func.argtypes = argtypes

            return

    def errget(self, code):
        """ gets error description """
        return self._dll__spam.sys_errget(code)

    def errset(self, code, msg):
        """ gets error description """
        lmsg = create_string_buffer(msg)
        self._dynmsgs__spam.append(lmsg)
        return self._dll__spam.sys_errset(code, lmsg)


def __caller(up = 0):
    """Get file name, line number, function name and
       source text of the caller's caller as 4-tuple:
       (file, line, func, text).
    """
    try:
        f = traceback.extract_stack(limit=up + 3)
        if f:
            return f[0]
    except:
        pass

    return ('', 0, '', None)


def debug2file(data, append = False):
    """Write to a temp file some data. Default file is /tmp/debug2file.txt
    data: Some str data
    append: append to end of file (append=True) or overwrite file
    
    TODO: Don't be a slackware, as me, use tempifile from Python stdlib
    """
    mode = 'a' if append else 'w'
    with open('/tmp/debug2file.txt', mode) as dbg:
        dbg.write(str(data))


def dump2pickle(fp, data, mode = 'wb'):
    """Dump objects to a pickle file that can be loaded in an external shell
    Supported types: dict, list, tuple, int, str, float
    fp = file name with full path to pickle file.
    data = data to dump
    mode = write once (default) or append
    
    Example:
    
    employees = get_employees_list()
    dump_to_pickle('/tmp/employees', employees, mode='wb')
    
    On console:
    
    >>> from pickle import load
    >>> emp = load('/tmp/employees')
    Voil\xc3\xa1!
    """
    if type(data) in [dict,
     list,
     tuple,
     int,
     str,
     float]:
        with open(fp, mode) as handle:
            pickle.dump(data, handle)


@contextmanager
def timeit(context = None):
    """Context manager to measure slices of code
    context: Text to identify the tracker
    
    Example:
    
    with timeit('measuring a simple "for" statement'):
        c = 0
        for i in range(100):
            c += 1
    """
    start_time = time()
    try:
        yield
    finally:
        args = (context, str(time() - start_time))
        msg = '#### Context: %s. That slice of code took %s seconds ####' % args
        sys_log_debug(msg)