# -*- coding: utf-8 -*-
# Module name: simplessl.py
# Module Description: Python wrapper for simplessl
#
# Copyright (C) 2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

"""
Python wrapper for the native "simplessl" library.
"""

import ctypes
import ctypes.util
import os.path
import sys
from cStringIO import StringIO
from ctypes import c_int32, c_char_p, c_uint32, c_void_p, Structure, POINTER, cdll, create_string_buffer, byref, string_at

_dll = None


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


#
# Structure definitions
#


class st_SimpleSSLData(Structure):
    _fields_ = [("data", c_char_p), ("size", c_uint32)]


st_SimpleSSLData_p = POINTER(st_SimpleSSLData)
st_SimpleSSLData_pp = POINTER(st_SimpleSSLData_p)

c_void_pp = POINTER(c_void_p)

#
# DLL Function definitions
#


_funcdefs = (
    ('simplessl_create', c_int32, (c_void_pp, c_char_p, c_uint32)),
    ('simplessl_setcertificate', c_int32, (c_void_p, c_char_p, c_int32, c_char_p, c_int32, c_char_p, c_uint32)),
    ('simplessl_connect', c_int32, (c_void_p, c_char_p, c_int32, c_char_p, c_uint32)),
    ('simplessl_write', c_int32, (c_void_p, c_char_p, c_uint32, c_char_p, c_uint32)),
    ('simplessl_readall', c_int32, (c_void_p, st_SimpleSSLData_pp, c_char_p, c_uint32)),
    ('simplessl_close', c_int32, (c_void_p, c_char_p, c_uint32)),
    ('simplessl_destroy', c_int32, (c_void_p, c_char_p, c_uint32)),
    ('simplessl_settimeout', None, (c_void_p, c_int32)),
    ('simplessl_setignoresslerrors', None, (c_void_p, c_int32)),
    ('simplessl_freedata', None, (c_void_p, st_SimpleSSLData_p)),
)


#
# Private functions
#


def _load_native():
    """ loads native libraries """
    global _load_native, _dll
    _libpath = _find_library("simplessl")
    if not _libpath:
        raise ImportError("Could not find library 'simplessl'.")
    _dll = cdll.LoadLibrary(_libpath)
    _load_native = None


def _init_dll():
    """
    Perform the DLL initialization inside a function, to avoid
    leaving variables in the module scope
    """
    global _init_dll, _dll
    if _load_native:
        _load_native()
    for name, restype, argtypes in _funcdefs:
        func = getattr(_dll, name, None)
        if func is None:
            raise ImportError(
                "Could not find function '%s' on 'simplessl' library." % name)
        func.restype = restype
        func.argtypes = argtypes
    _init_dll = None


#
# Public APIs
#


class SimpleSSL:

    """Represents an SSL connection"""

    def __init__(self, timeout=None, ignore_ssl_err=False):
        global _dll
        if _init_dll:
            _init_dll()
        self._errmsg = create_string_buffer("", 512)
        self._errsize = 512
        self._pconn = c_void_p(0)
        self._call('simplessl_create', byref(self._pconn))
        if timeout:
            self.settimeout(timeout)
        if ignore_ssl_err:
            _dll.simplessl_setignoresslerrors(self._pconn, 1)

    def connect(self, hostname, port=443):
        """
        Connects to a host using SSL.
        @param hostname: hostname to connect to (E.g.: "www.example.com", or "127.0.0.1")
        @param port: port to conect to (E.g.: 443)
        """
        self._call('simplessl_connect', self._pconn, hostname, port)

    def write(self, data):
        """
        Writes data over the SSL connection.
        @param data: data buffer to be written
        """
        data = str(data)
        self._call('simplessl_write', self._pconn, data, len(data))

    def read(self):
        """
        Reads ALL data from the SSL connection (until the connection is closed).
        """
        global _dll
        pdata = st_SimpleSSLData_p()
        self._call('simplessl_readall', self._pconn, byref(pdata))
        data = pdata.contents
        res = string_at(data.data, data.size)
        _dll.simplessl_freedata(self._pconn, pdata)
        return res

    def settimeout(self, timeout):
        """
        Sets the timeout for blocking IO operations
        @param timeout: timeout in seconds (E.g.: 10.00)
        """
        global _dll
        if timeout:
            _dll.simplessl_settimeout(self._pconn, int(float(timeout) * 1000))

    def setcertificate(self, cert, key):
        """
        Sets the client certificate and/or key to be used on this connection.
        This MUST be called before #connect.
        @param cert: the certificate string (PEM-formatted)
        @param key: the RSA private key string (PEM-formatted)
        """
        szcert = len(cert) if cert else 0
        szkey = len(key) if key else 0
        self._call(
            'simplessl_setcertificate', self._pconn, cert, szcert, key, szkey)

    def close(self):
        """
        Closes the SLL connection
        """
        self._call('simplessl_close', self._pconn)

    def send(self, data):
        """Same as #write, but returns len(data)"""
        self.write(data)
        return len(data)

    def sendall(self, data):
        """alias to #write"""
        self.write(data)

    def makefile(self, mode=None, bufsize=None):
        """returns a file-like object with the contents of #read"""
        data = self.read()
        return StringIO(data)

    def _call(self, func, *args):
        global _dll
        args = list(args) + [self._errmsg, self._errsize]
        res = _dll[func](*args)
        if res != 0:
            msg = self._errmsg.raw
            end = msg.index('\0')
            msg = "%s: %s" % (res, msg[:end])
            raise SimpleSSLError(msg)


#
# Exceptions
#


class SimpleSSLError(Exception):
    pass
