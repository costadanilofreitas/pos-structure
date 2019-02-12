# -*- coding: utf-8 -*-
# Module name: pafecf.py
# Module Description: Contains helper functions and definitions for the Brazilian PAF-ECF
#
# Copyright (C) 2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

import sys
import os
import hashlib
import types

__all__ = ('PAF_ECF',)


class PAF_ECF:

    """
    Contains functions and definitions for the Brazilian "PAF-ECF"
    """
    # The PAF-ECF specification version implemented by this software.
    # This must be updated every time a new specification is released
    # by the Brazilian government!
    SPEC_VERSION_FULL = "02.04"  # "01.11"
    SPEC_VERSION = SPEC_VERSION_FULL.replace(".", "")

    # The name of the "md5 list" file
    SW_MD5_FILE = "MD5.txt"

    # Main application module (executable)
    main_module = "pafecf/mwapp"

    # Extra executables necessary for the PAF-ECF to work
    extra_exe = ["pafecf/account", "pafecf/boss", "pafecf/genclient", "pafecf/gencopy", "pafecf/genserver", "pafecf/guicomp", "pafecf/httpcomp", "pafecf/hv", "pafecf/hvmon", "pafecf/i18n",
                 "pafecf/npersistagent", "pafecf/npersistcomp", "pafecf/peripherals", "pafecf/posctrl", "pafecf/salectrlcomp", "pafecf/storecfg", "pafecf/taxcalc" ]

    # Extra libraries necessary for the PAF-ECF to work
    extra_lib = ["pafecf/apr_dbd_persistcomp", "pafecf/apr_dbd_sqlite3", "pafecf/cashdrawer", "pafecf/cfgtools", "pafecf/drvvirtual", "pafecf/eft", "pafecf/expat",
                 "pafecf/hvudp", "pafecf/libapr-1", "pafecf/libapriconv-1", "pafecf/libaprutil-1", "pafecf/libipcqueue", "pafecf/linedisplay", "pafecf/msgbus",
                 "pafecf/msr", "pafecf/msrkeyboard", "pafecf/printer", "pafecf/prnlpt", "pafecf/QtCore4", "pafecf/QtGui4", "pafecf/QtNetwork4", "pafecf/QtWebKit4",
                 "pafecf/QtXmlPatterns4", "pafecf/scew", "pafecf/simpleinput", "pafecf/simplessl", "pafecf/sqlite3", "pafecf/sysprn", "pafecf/systools", "pafecf/tcputil",
                 "pafecf/urlcamera", "pafecf/xmldbext", "pafecf/zlib"]

    # Extra files necessary for the PAF-ECF to work
    extra = ["pafecf/gui_pos.zip", "pafecf/common.pypkg", "pafecf/migratedb.pypkg", "pafecf/pyscripts.pypkg", "pafecf/reports.pypkg", "pafecf/runpackage.py"]

    class PublicKey:

        """
        Public PAF-ECF key
        """
        # The public exponent
        e = 76420703824601684219886586748058597574083417065985394987132331627640370161737L
        # modulus (q*p)
        n = 104071016761429183205283135945131609742114373562692592639793496669859483943995712893268175095172654248666250246286322848299511207644872358140273222244096913844222053055526382915160941445256928525244438529491778624938712481722778335279469147540018869154337083799570919902192228410808241669537719631343741918381L

    @classmethod
    def get_EAD_signature(clazz, data):
        """
        Computes the PAF-ECF "EAD" block signature for the given data.
        This is basically the RSA signature from the MD5 hash of this data.
        """
        class PrivateKey:
            # The private exponent (1024 bits)
            d = 42308559333659527810921233808780448046657567781370280339201133734203436849887609704317293921567394736853447958170606956172791533214344691010234233421179444630470115409600538031733727546706300784057908884333119226526710864550320806676357378942054483711972837940624789541275472503978326618065695638101197730105L
            # First random prime number
            q = 13083244922149364554711361284213333156589877975871009208198689244717951171073206458288892964984921485699055206061588884508738670205298290251922530968680477L
            # Second random prime number
            p = 7954526371759767237645347355166867282961755676164189835093522752651129483874906845867082267699617142615820461956986245232580350390100858471422685944230353L
            # modulus (q*p)
            n = 104071016761429183205283135945131609742114373562692592639793496669859483943995712893268175095172654248666250246286322848299511207644872358140273222244096913844222053055526382915160941445256928525244438529491778624938712481722778335279469147540018869154337083799570919902192228410808241669537719631343741918381L
        if isinstance(data, unicode):
            data = data.encode("UTF-8")
        if not isinstance(data, str):
            raise TypeError("Expected str or unicode, not %s" % type(data))
        # Compute the block to be signed, as described in
        # [http://www.fazenda.gov.br/confaz/confaz/Atos/Atos_Cotepe/2008/AC006_08.htm] - ANEXO VIII
        md5 = hashlib.md5(data).digest()
        block = '\x10' + md5 + (' ' * 111)
        if len(block) != 128:
            raise AssertionError("Block to encrypt must be 128-bytes long")
        # The RSA signature algorithm is so simple that we don't really need a library to handle it
        # See [http://en.wikipedia.org/wiki/RSA] (in the "Signing messages" section) for more details
        # RSA sign: (message_integer**d)%n
        sigint = pow(_bytes2int(block), PrivateKey.d, PrivateKey.n)
        # Convert to a 256-characters long HEX string
        sighex = '%0256x' % sigint
        # Generate the EAD record
        EAD = "EAD%s" % sighex
        return EAD

    @classmethod
    def get_main_module(clazz, env):
        """Retrieve the name of the main executable module"""
        return _full_exe(clazz.main_module, env)

    @classmethod
    def get_extra_modules(clazz, env):
        """Retrieve a list with all the extra binary modules used by the system"""
        return [_full_exe(exe, env) for exe in clazz.extra_exe] + [_full_lib(lib, env) for lib in clazz.extra_lib] + clazz.extra

    @classmethod
    def get_all_modules(clazz, env):
        """Retrieve a list with all binary modules used by the system - including the main module"""
        return [clazz.get_main_module(env)] + clazz.get_extra_modules(env)

    @classmethod
    def get_MD5(clazz, filename):
        """Calculate the MD5 of a file"""
        md5 = hashlib.md5()
        with open(filename, "rb") as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest().upper()

    @classmethod
    def get_software_version(clazz):
        """Retrieve the application version"""
        return os.environ.get("MWAPP_VERSION_STRING", "")

    @classmethod
    def get_paf_cert_date(clazz):
        """Retrieve the paf certification date"""
        return os.environ.get("MWAPP_PAF_CERT_DATE", "")

    @classmethod
    def get_paf_cert_number(clazz):
        """Retrieve the paf certification number"""
        return os.environ.get("MWAPP_PAF_CERT_NUMBER", "")

#
# Platform-specific helpers
#


def _full_exe(base, env):
    if env.startswith("win"):
        return "%s.exe" % base
    else:
        return base


def _full_lib(base, env):
    if env.startswith("win"):
        return "%s.dll" % base
    else:
        if base.startswith("lib"):
            return "%s.so" % base
        return "lib%s.so" % base

#
# Bytes conversion helpers
#


def _bytes2int(bytes):
    """Converts a list of bytes or a string to an integer

    >>> (128*256 + 64)*256 + + 15
    8405007
    >>> l = [128, 64, 15]
    >>> _bytes2int(l)
    8405007
    """
    if not (isinstance(bytes, types.ListType) or isinstance(bytes, types.StringType)):
        raise TypeError("You must pass a string or a list")
    # Convert byte stream to integer
    integer = 0
    for byte in bytes:
        integer *= 256
        if isinstance(byte, types.StringType):
            byte = ord(byte)
        integer += byte
    return integer


def _int2bytes(number):
    """Converts a number to a string of bytes

    >>> _bytes2int(_int2bytes(123456789))
    123456789
    """
    if not (isinstance(number, types.LongType) or isinstance(number, types.IntType)):
        raise TypeError("You must pass a long or an int")
    string = ""
    while number > 0:
        string = "%s%s" % (chr(number & 0xFF), string)
        number /= 256
    return string
