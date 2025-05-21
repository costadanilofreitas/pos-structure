# -*- coding: utf-8 -*-
# Module name: msgbus.py
# Module Description: Python wrapper for msgbus
#
# Copyright © 2008 MWneo Corporation
#
# $Id: msgbus.py 14404 2014-04-08 11:53:45Z rrocha $
# $Revision: 14404 $
# $Date: 2014-04-08 08:53:45 -0300 (Tue, 08 Apr 2014) $
# $Author: rrocha $

"""
Python wrapper for native message-bus library.

This module wraps all native message-bus functions with a object-oriented API.
All "release" related functions are not wrapped because this module automatically
handles the native releasing thru python garbage collector.

When this module is imported, the native "msgbus" library will be loaded, so it is
possible that an exception is raised during the module initialization (if any problem
happen loading the native library).

Minimal "Hello world" example:
>>> ctx = MBEasyContext("python test")
>>> while True:
        msg = ctx.MB_EasyGetMessage()
        if not msg:
            break
        print "Received message. Token: %d. Format: %d. Data: %s."%(msg.token,msg.format,msg.data)
        ctx.MB_EasyReplyMessage(msg)
>>> print "Done!"

"""

import httplib
import socket
import traceback
import ctypes
import ctypes.util
import os.path
import base64
import sys
from ctypes import c_int, c_void_p, c_char_p, c_int32, c_uint32, c_int64, Structure, POINTER, string_at, cdll
from syserrors import SE_SUCCESS, SE_TIMEOUT, SE_NOTFOUND, SE_UNDEFINED
from systools import sys_errget

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


# Startup flags
SU_FRESH = 0x00000001

# START OF TOKEN LIST
TK_SYS_ACK = 0xF0100001
TK_SYS_NAK = 0xF0100002
TK_SYS_CHECKFORUPDATES = 0x00100003
TK_HV_COMPSTART = 0x00200001
TK_HV_COMPSTOP = 0x00200002
TK_HV_COMPKILL = 0xF0200002
TK_HV_COMPLIST = 0x00200003
TK_HV_QUERY_SERVICE = 0x00200004
TK_HV_FIND_SERVICE = 0x00200005
TK_HV_QUERY_BY_TYPE = 0x00200006
TK_HV_START_COMP = 0x00200007
TK_HV_SERVICEONLINE = 0x00200008
TK_HV_SERVICEOFFLINE = 0x00200009
TK_HV_RESTART = 0x0020000A
TK_HV_GLOBALRESTART = 0x0020000B
TK_HV_GETSTATE = 0x0020000C
TK_HV_SETSTATE = 0x0020000D
TK_HV_LOG = 0x0020000E
TK_HV_GETLICENSE = 0x0020000F
TK_HV_LOGLEVEL = 0xF0200010
TK_HV_LISTHVS = 0x00200020
TK_HV_CHECK_LICENSE_SIGNATURE = 0x00200030
TK_CMP_TERM_NOW = 0xF0300001
TK_CMP_GETSERVICES = 0xF0300002
TK_CMP_GETDEPENDS = 0xF0300003
TK_CMP_REGSERVICE = 0xF0300004
TK_CMP_START = 0xF0300005
TK_CMP_MESSAGE = 0xF0300006
TK_EVT_EVENT = 0xF0400001
TK_EVT_SUBSCRIBE = 0xF0400002
TK_EVT_UNSUBSCRIBE = 0xF0400003
TK_EVT_RUNTESTS = 0xF0400004
TK_EVT_GETLISTENERS = 0xF0400005
TK_POS_GETMODEL = 0xF0500001
TK_POS_SETSCREEN = 0xF0500002
TK_POS_EXECUTEACTION = 0xF0500003
TK_POS_MODELSETCUSTOM = 0xF0500004
TK_POS_SETINFOMSG = 0xF0500005
TK_POS_SHOWDIALOG = 0xF0500006
TK_POS_DIALOGRESP = 0xF0500007
TK_POS_BUSINESSBEGIN = 0xF0500008
TK_POS_BUSINESSEND = 0xF0500009
TK_POS_USERLOGIN = 0xF050000A
TK_POS_USERPAUSE = 0xF050000B
TK_POS_USERLOGOUT = 0xF050000C
TK_POS_SETDEFSERVICE = 0xF050000D
TK_POS_SETLANG = 0xF050000E
TK_POS_SETMAINSCREEN = 0xF050000F
TK_POS_SETPOD = 0xF0500010
TK_POS_SETFUNCTION = 0xF0500011
TK_POS_USEROPEN = 0xF0500012
TK_POS_SETMODIFIERSDATA = 0xF0500013
TK_POS_ASYNCACTION = 0xF0500014
TK_POS_GETSTATE = 0xF0500015
TK_POS_GETCONFIG = 0xF0500016
TK_POS_LISTUSERS = 0xF0500017
TK_POS_SETRECALLDATA = 0xF0500018
TK_POS_GETPOSLIST = 0xF0500019
TK_POS_UPDATEDIALOG = 0xF050001A
TK_KDS_GETMODEL = 0xF0B00001
TK_KDS_UPDATEVIEW = 0xF0B00002
TK_KDS_REFRESH = 0xF0B00003
TK_KDS_REFRESH_END = 0xF0B00004
TK_KDS_SET_PROD_STATE = 0xF0B00005
TK_KDS_UNDO_SERVE = 0xF0B00006
TK_KDS_CHANGE_VIEW = 0xF0B00007
TK_KDS_TOGGLE_TAG_LINE = 0xF0B00008
TK_KDS_GLOBAL_SERVE = 0xF0B00009
TK_KDS_REFRESH_VIEW = 0xF0B00010
TK_KDS_DISABLE_VIEW = 0xF0B00011
TK_KDS_UPDATE_INFO = 0xF0B00012
TK_KDS_ENABLE_VIEW = 0xF0B00013
TK_KDS_RELOAD = 0xF0B00014
TK_KIOSK_GETMODEL = 0xF1D00001
TK_KIOSK_SETLANG = 0xF1D00002
TK_KIOSK_GETSTATE = 0xF1D00003
TK_KIOSK_SETSTATE = 0xF1D00004
TK_KIOSK_CHECKFORUPDATES = 0xF1D01001
TK_KIOSK_EXECUTEACTION = 0xF1D01002
TK_KIOSK_PROVIDER_RESERVE = 0xF1D02001
TK_KIOSK_PROVIDER_CONFIRM = 0xF1D02002
TK_KIOSK_PROVIDER_DISMISS = 0xF1D02003
TK_KIOSK_TRANSACTION_PICTURE = 0xF1D03001
TK_FISCAL_CMD = 0xF0600001
TK_PRN_PRINT = 0xF0600101
TK_PRN_GETSTATUS = 0xF0600102
TK_CDRAWER_OPEN = 0xF0600201
TK_CDRAWER_GETSTATUS = 0xF0600202
TK_LDISP_WRITE = 0xF0600301
TK_LDISP_MARQUEE = 0xF0600302
TK_MSR_REQUESTSWIPE = 0xF0600402
TK_COIN_DISPENSE = 0xF0600801
TK_COIN_GETSTATUS = 0xF0600802
TK_COIN_SETUP = 0xF0600803
TK_COIN_RESET = 0xF0600804
TK_COIN_EXAMINE = 0xF0600805
TK_COIN_ADJUST = 0xF0600806
TK_COIN_COLLECT = 0xF0600807
TK_IMGCAP_CAPTURE = 0xF0600901
TK_BUZZER_SOUND = 0xF0600B01
TK_CTRLUNIT_REGISTER_SALE = 0xF0600B01
TK_CTRLUNIT_REGISTER_RETURN = 0xF0600B02
TK_CTRLUNIT_WRITE_JOURNAL = 0xF0600B03
TK_DRV_IOCTL = 0xF060FFFF
TK_I18N_GETTABLE = 0x00700001
TK_I18N_GETMSG = 0x00700002
TK_I18N_TRANSLATE = 0x00700003
TK_I18N_GETLANGS = 0x00700004
TK_I18N_GETTABLEJSON = 0x00700005
TK_L10N_TOCURRENCY = 0x00700006
TK_L10N_TONUMBER = 0x00700007
TK_L10N_TODATE = 0x00700008
TK_L10N_TOTIME = 0x00700009
TK_L10N_TODATETIME = 0x0070000A
TK_L10N_FROMCURRENCY = 0x0070000B
TK_L10N_FROMNUMBER = 0x0070000C
TK_L10N_FROMDATE = 0x0070000D
TK_L10N_FROMTIME = 0x0070000E
TK_L10N_FROMDATETIME = 0x0070000F
TK_PERSIST_QUERYEXEC = 0x00800001
TK_PERSIST_CONNALLOC = 0x00800002
TK_PERSIST_CONNRELEASE = 0x00800003
TK_PERSIST_SCRIPTEXEC = 0x00800004
TK_PERSIST_PROCEXEC = 0x00800005
TK_PERSIST_EXPORTDB = 0x00800006
TK_PERSIST_IMPORTDB = 0x00800007
TK_PERSIST_LISTDBS = 0x00800008
TK_PERSIST_GETINSTNBR = 0x00800009
TK_PURGE_DB = 0x0080000A
TK_PERSIST_INITTHRDTERM = 0x0080000B
TK_PERSIST_INITINPROGRESS = 0x0080000C
TK_PERSIST_SEQUENCER_INCREMENT = 0x0080000D
TK_PERSIST_GET_PROCEDURES_LIST = 0x0080000E
TK_PERSIST_GET_PROCEDURE_PARAMS = 0x0080000F
TK_PERSIST_SEQUENCER_RESET = 0x00800010
TK_PERSIST_CHECKCONNECTION = 0x00800011
TK_REPLICATE = 0xF0800008
TK_REPLICA_ACQUIRE = 0xF0800009
TK_REPLICA_LISTDBS = 0xF0800010
TK_REPLICA_GETCHKPNT = 0xF0800011
TK_REPLICA_GETFAILOVERCHKPNT = 0xF0800012
TK_REPLICA_GETUSERVERSION = 0xF0800013
TK_SLCTRL_PMGR_MAINMENU = 0x00900001
TK_SLCTRL_PMGR_CUSTOMPARAM = 0x00900002
TK_SLCTRL_PMGR_PRODUCTSBYTAGS = 0x00900003
TK_SLCTRL_PMGR_PRODUCTDIM = 0x00900004
TK_SLCTRL_OMGR_DOSALE = 0x00A00001
TK_SLCTRL_OMGR_ORDERPICT = 0x00A00002
TK_SLCTRL_OMGR_VOIDLINE = 0x00A00003
TK_SLCTRL_OMGR_VOIDORDER = 0x00A00004
TK_SLCTRL_OMGR_LISTOPTIONS = 0x00A00005
TK_SLCTRL_OMGR_ORDERTOTAL = 0x00A00006
TK_SLCTRL_OMGR_CLEAROPTION = 0x00A00007
TK_SLCTRL_OMGR_SPLITORDER = 0x00A00008
TK_SLCTRL_OMGR_SPLITORDERLINE = 0x00A00009
TK_SLCTRL_OMGR_DOOPTION = 0x00A0000A
TK_SLCTRL_OMGR_STOREORDER = 0x00A0000B
TK_SLCTRL_OMGR_RECALLORDER = 0x00A0000C
TK_SLCTRL_OMGR_LISTORDERS = 0x00A0000D
TK_SLCTRL_OMGR_CHANGEQTY = 0x00A0000E
TK_SLCTRL_OMGR_ORDERREOPEN = 0x00A0000F
TK_SLCTRL_OMGR_DOTENDER = 0x00A00010
TK_SLCTRL_OMGR_CLEARTENDERS = 0x00A00011
TK_SLCTRL_OMGR_LISTMODIFIERS = 0x00A00012
TK_SLCTRL_OMGR_CHANGEMODIFIER = 0x00A00013
TK_SLCTRL_OMGR_CHANGEDIMENSION = 0x00A00014
TK_SLCTRL_OMGR_RESETCURRORDER = 0x00A00015
TK_SLCTRL_OMGR_SETLSTSALELINE = 0x00A00016
TK_SLCTRL_OMGR_UPDPROPERTIES = 0x00A00017
TK_SLCTRL_OMGR_CREATEORDER = 0x00A00018
TK_SLCTRL_OMGR_CHANGEMODIFIERS = 0x00A00019
TK_SLCTRL_OMGR_VOIDHISTORY = 0x00A0001A
TK_SLCTRL_OMGR_PRICEOVERWRITE = 0x00A0001B
TK_SLCTRL_OMGR_LISTOPTSOLUTIONS = 0x00A0001C
TK_SLCTRL_OMGR_SETCUSTOMPROPERTY = 0x00A0001D
TK_SLCTRL_OMGR_GETCUSTOMPROPERTY = 0x00A0001E
TK_SLCTRL_OMGR_LIST_DISCOUNTS = 0x00A0001F
TK_SLCTRL_OMGR_APPLY_DISCOUNT = 0x00A00020
TK_SLCTRL_OMGR_CLEAR_DISCOUNT = 0x00A00021
TK_SLCTRL_OMGR_MERGE_ORDERS = 0x00A00022
TK_SLCTRL_OMGR_EXTRAMODIFIERS = 0x00A00023
TK_SLCTRL_OMGR_DOMULTIOPTIONS = 0x00A00024
TK_SLCTRL_OMGR_ADDCOMMENT = 0x00A00025
TK_SLCTRL_OMGR_DELCOMMENT = 0x00A00026
TK_SLCTRL_OMGR_UPDCOMMENT = 0x00A00027
TK_SLCTRL_OMGR_SETCUSTOMPROPERTIES = 0x00A00028
TK_SLCTRL_OMGR_FRACTIONATELINE = 0x00A00029
TK_SLCTRL_OMGR_REVERTLINEFRACTION = 0x00A00030
TK_SLCTRL_OMGR_RESETORDERTENDER = 0x00A00031
TK_SLCTRL_RESET = 0x02600001
TK_PROD_REFRESHVIEW = 0x00C00001
TK_PROD_SETORDERSTATE = 0x00C00002
TK_PROD_CRASHPOINT = 0x00C00003
TK_PROD_CAPTUREIMAGE = 0x00C00004
TK_PROD_RETRIEVEIMAGE = 0x00C00005
TK_PROD_SIDEONOFF = 0x00C00006
TK_PROD_UNDOSERVE = 0x00C00007
TK_PROD_TOGGLETAGLINE = 0x00C00008
TK_PROD_GLOBAL_SERVE = 0x00C00009
TK_PROD_DISABLE_VIEW = 0x00C00010
TK_PROD_ENABLE_VIEW = 0x00C00011
TK_PROD_REDIRECT_BOX = 0x00C00012
TK_PROD_RESTORE_BOX = 0x00C00013
TK_REPORT_GENERATE = 0x00D00001
TK_ACCOUNT_TRANSFER = 0x00E00001
TK_ACCOUNT_GETTRANSFERS = 0x00E00002
TK_ACCOUNT_GETTOTALS = 0x00E00003
TK_ACCOUNT_GIFTCARDACTIVITY = 0x00E00004
TK_ACCOUNT_EFTACTIVITY = 0x00E00005
TK_EFT_REQUEST = 0x00F00001
TK_GENESIS_GETVERSION = 0x01000001
TK_GENESIS_LISTFILES = 0x01000002
TK_GENESIS_GETFILE = 0x01000003
TK_GENESIS_LISTPKGS = 0x01000004
TK_GENESIS_APPLYUPDATE = 0x01000005
TK_GENESIS_ROLLBACKUPDATE = 0x01000006
TK_TIMEPUNCH_OPER = 0x01100001
TK_TIMEPUNCH_REPORT = 0x01100002
TK_TIMEPUNCH_GETJOBCODES = 0x01100003
TK_USERCTRL_AUTHENTICATE = 0x01200001
TK_USERCTRL_GETINFO = 0x01200002
TK_USERCTRL_GETINFO_BADGE = 0x01200003
TK_STORECFG_GET = 0x01300001
TK_STORECFG_GETFULL = 0x01300002
TK_STORECFG_SET = 0x01300003
TK_AUDITLOG_RESYNC = 0xF1400001
TK_BOINVENTORY_UNUSED = 0x01500000
TK_BOINVENTORY_MANAGE_SUPPLIER = 0x01500001
TK_BOINVENTORY_MANAGE_SUPPLIER_PRODUCTS = 0x01500002
TK_BOINVENTORY_MANAGE_SUPPLIER_INVOICES = 0x01500003
TK_BOINVENTORY_MANAGE_STORAGE_AREAS = 0x01500004
TK_BOINVENTORY_MANAGE_DEPARTMENTS = 0x01500005
TK_BOINVENTORY_MANAGE_GROUPS = 0x01500006
TK_BOINVENTORY_MANAGE_ITEMS = 0x01500007
TK_BOINVENTORY_MANAGE_BOM = 0x01500008
TK_BOINVENTORY_MANAGE_INVENTORY_COUNTS = 0x01500009
TK_BOINVENTORY_IMPORT_POS_SALES = 0x0150000A
TK_BOINVENTORY_INVENTORY_CONTROL = 0x0150000B
TK_BOINVENTORY_INVOICES_AVAILABLE = 0x0150000C
TK_BOINVENTORY_SALES_AVAILABLE = 0x0150000D
TK_BOINVENTORY_INVENTORY_TRANSACTION = 0x0150000E
TK_BOINVENTORY_DELIVERY_TRANSACTION = 0x0150000F
TK_BOINVENTORY_POS_SALES_TRANSACTION = 0x01500010
TK_BOINVENTORY_DELIVERY_TRANSACTION_DETAILS = 0x01500011
TK_BOINVENTORY_POS_SALES_TRANSACTION_DETAILS = 0x01500012
TK_BOINVENTORY_COUNT_ADJUSTMENT_TRANSACTION = 0x01500013
TK_BOINVENTORY_DELIVERY_ADJUSTMENT_TRANSACTION = 0x01500014
TK_BOINVENTORY_SUBINVENTORY_TRANSFER_TRANSACTION = 0x01500015
TK_BOINVENTORY_INBOUND_TRANSFER_TRANSACTION = 0x01500016
TK_BOINVENTORY_OUTBOUND_TRANSFER_TRANSACTION = 0x01500017
TK_BOINVENTORY_SUPPLIER_RETURN_TRANSACTION = 0x01500018
TK_BOINVENTORY_WIP_SCRAP_TRANSACTION = 0x01500019
TK_BOINVENTORY_INVENTORY_RESET = 0x0150001A
TK_BOINVENTORY_REPORTS = 0x0150001B
TK_BOINVENTORY_MANAGE_ASSEMBLY = 0x0150001C
TK_BOINVENTORY_MANAGE_ITEM_PACKAGES = 0x0150001D
TK_BOINVENTORY_MANAGE_PLU_LIST = 0x0150001E
TK_BOCASH_REPORTS = 0x01600000
TK_BOCASH_MANAGE_STORECFG = 0x01600001
TK_BOCASH_MANAGE_BUSINESSWEEK = 0x01600002
TK_BOCASH_MANAGE_DRAWERCOUNT_TEMPLATE = 0x01600003
TK_BOCASH_MANAGE_BUSINESSDATE = 0x01600004
TK_BOCASH_POSEVENTS_DAYOPEN = 0x01600005
TK_BOCASH_POSEVENTS_DAYCLOSE = 0x01600006
TK_BOCASH_POSEVENTS_SKIM = 0x01600007
TK_BOCASH_POSEVENTS_DRAWERCHANGE = 0x01600008
TK_BOCASH_MANAGE_DRAWERCOUNT = 0x01600009
TK_BOCASH_MANAGE_DRAWERCOUNT_DETAILS = 0x0160000A
TK_BOCASH_MANAGE_TRANSACTIONS = 0x0160000B
TK_BOCASH_MANAGE_TRANSACTION_DETAILS = 0x0160000C
TK_BOCASH_POSEVENTS_HISTORY = 0x0160000D
TK_BOCASH_FORCE_WEEK_CLOSE = 0x0160000E
TK_BOREPORT_REPORTS = 0x01800000
TK_BOREPORT_MANAGE_TEMPLATE = 0x01800001
TK_BOREPORT_MANAGE_WORKBOOK = 0x01800002
TK_BOREPORT_MANAGE_WORKSHEET = 0x01800003
TK_BOREPORT_MANAGE_WORKSHEET_CELLS = 0x01800004
TK_BOREPORT_WORKBOOK_FILE = 0x01800005
TK_BOREPORT_WORKBOOK_SOLVER = 0x01800006
TK_BOREPORT_WORKBOOK_PREVIEW = 0x01800007
TK_BOREPORT_GETCONFIG = 0x01800008
TK_BOACCOUNT_REPORTS = 0x01700000
TK_BOACCOUNT_MANAGE_TRNTYPE = 0x01700001
TK_BOACCOUNT_MANAGE_CHARTOFACCOUNTS = 0x01700002
TK_BOACCOUNT_MANAGE_JOURNALTEMPLATE = 0x01700003
TK_BOACCOUNT_MANAGE_JOURNAL = 0x01700004
TK_BOACCOUNT_MANAGE_TRIALBALANCE = 0x01700005
TK_BOLABOR_REPORTS = 0x01C00000
TK_BOLABOR_MANAGE_EMPLOYEES = 0x01C00001
TK_BOLABOR_MANAGE_TIMEPUNCHES = 0x01C00002
TK_BOLABOR_MANAGE_EMPLOYEE_CUSTOMDATA = 0x01C00003
TK_CASHLESS_REPORT = 0x01900001
TK_GUI_REQUESTFOCUS = 0x01A00001
TK_GUI_SETURL = 0x01A00002
TK_GUI_EVALJS = 0x01A00003
TK_GUI_MINIMIZE = 0x01A00004
TK_CALLCENTER_GETSTATUS = 0x01B00001
TK_CALLCENTER_AGTLOGIN = 0x01B00002
TK_CALLCENTER_SETAGTSTATE = 0x01B00003
TK_CALLCENTER_NEWCALL = 0x01B00004
TK_CALLCENTER_CALLENDED = 0x01B00005
TK_CALLCENTER_AGTSTATECHANGED = 0x01B00006
TK_CALLCENTER_RECONNECT = 0x01B00007
TK_CALLCENTER_SETVOLUME = 0x01B00008
TK_CALLCENTER_TRANSFER = 0x01B00009
TK_CALLCENTER_HEARTHBEAT = 0x01B0000A
TK_CALLCENTER_EXITAPP = 0x01B0000B
TK_CALLCENTER_SETFAILOVER = 0x01B0000C
TK_CALLCENTER_SHOWALERT = 0x01B0000D
TK_CALLCENTER_MANAGEBTREST = 0x01B0000E
TK_LS_RETRIEVE_CACHE = 0x01E00001
TK_LS_STORE_CACHE = 0x01E00002
TK_LS_CREATE_SESSION = 0x01E00003
TK_LS_STORE_PURCHASE = 0x01E00004
TK_LS_VOID_PURCHASE = 0x01E00005
TK_BUF_BUFFER_PURCHASE = 0x01F00001
TK_BUF_PAY_ORDER = 0x01F00002
TK_BUF_STORE_API_CALL = 0x01F00003
TK_BUF_FINISH_ORDER = 0x01F00004
TK_ML_REFRESH_CACHE = 0x02000001
TK_KIOSKCTRL_DBUPDATE = 0x02100001
TK_KIOSKCTRL_GENESISUPDATE = 0x02100002
TK_KIOSKCTRL_IMAGESUPDATE = 0x02100003
TK_CATERING_NEWEVENT = 0x02200001
TK_CATERING_STORECUSTOMER = 0x02200002
TK_CATERING_SEARCHCUSTOMER = 0x02200003
TK_CATERING_UPDATECUSTOMER = 0x02200004
TK_CATERING_UPDATEEVENT = 0x02200005
TK_CATERING_UPDATEBILLINGID = 0x02200006
TK_CATERING_ORDERPICT_TO_JSON = 0x02200007
TK_CATERING_GETCAFEINFO = 0x02200008
TK_CATERING_GETEVENT = 0x02200009
TK_ROPECTRL_SEND_XML = 0x02300001
TK_ROPECTRL_ROPE_XML = 0x02300002
TK_BOH_MESSAGE = 0x02400001
TK_BOH_UPLOADORDER = 0x02400002
TK_LOYALTY_AUTHENTICATE = 0x02500001
TK_LOYALTY_BALANCE = 0x02500002
TK_LOYALTY_APPLY = 0x02500003
TK_LOYALTY_VOID = 0x02500004
TK_LOYALTY_REFUND = 0x02500005
TK_LOYALTY_COMMAND = 0x02500006
# END OF TOKEN LIST

# Data formats
FM_UNDEFINED = 0x00000000
FM_XML = 0x00000001
FM_PARAM = 0x00000002
FM_ADDR_PORT = 0x00000003
FM_INT32 = 0x00000004
FM_INT64 = 0x00000005
FM_STRING = 0x00000006
FM_STR_ARRAY_PIPE = 0x00000007
FM_IMG_JPG = 0x00000008
FM_IMG_PNG = 0x00000009
FM_IMG_GIF = 0x0000000A
FM_PDF = 0x0000000B
FM_SWAGGER = 0x0000000C

#
# Structure definitions
#


class st_msg(Structure):
    _fields_ = [("sign", c_int32),       # signature
                ("size", c_int32),       # data size
                ("token", c_uint32),     # token
                ("format", c_int32),     # format
                ("destname", c_char_p),  # destination service name (optional)
                ("data", c_void_p),      # data
                ("trailer", c_int32),    # trailer
                ("crc", c_int32),        # crc32
                ("remotehost", c_char_p)]  # remote host name or IP address - for incoming messages only


st_msg_p = POINTER(st_msg)


class st_service(Structure):
    _fields_ = [("addr", c_char_p),      # ip addr
                ("port", c_int32),       # port
                ("name", c_char_p), ]    # service name


st_service_p = POINTER(st_service)


class st_easymb(Structure):
    _fields_ = [("pctx", c_void_p),      # a plain message bus context created by MB_EasyInitialize
                ("ser", st_service_p),   # service information
                ("hv", st_service_p),    # hypervisor information
                ("opaque", c_void_p)]    # reserved for internal use


st_easymb_p = POINTER(st_easymb)

c_enun = c_int
c_enun_p = POINTER(c_enun)
c_int_p = POINTER(c_int)
c_int32_p = POINTER(c_int32)
c_char_pp = POINTER(c_char_p)

#
# DLL Function definitions
#

_funcdefs = (
    ('MB_CreateService', st_service_p, (c_char_p, c_int32, c_void_p, c_char_p, c_int32)),
    ('MB_Initialize', c_void_p, (st_service_p, c_char_p, c_enun_p, c_char_p, c_int32)),
    ('MB_GetMessage', st_msg_p, (c_void_p, c_enun, c_enun, c_char_p, c_int32)),
    ('MB_SendMessage', st_msg_p, (c_void_p, st_service_p, c_int32, c_enun, c_enun, c_char_p, c_int64, c_enun_p, c_char_p, c_int32)),
    ('MB_SendOneWayMessage', None, (c_void_p, st_service_p, c_int32, c_enun, c_enun, c_char_p, c_int64, c_enun_p, c_char_p, c_int32)),
    ('MB_PeekMessage', st_msg_p, (c_void_p, c_enun, c_enun, c_char_p, c_int32)),
    ('MB_ReplyMessage', c_int32, (c_void_p, st_msg_p, c_int32, c_enun, c_char_p)),
    ('MB_LocateService', st_service_p, (c_void_p, st_service_p, c_char_p, c_int32, c_enun_p, c_char_p, c_int32)),
    ('MB_ReleaseService', c_enun, (st_service_p,)),
    ('MB_Finalize', c_enun, (c_void_p,)),
    ('MB_FinalizeAll', c_enun, ()),
    ('MB_ReleaseMessage', None, (st_msg_p,)),
    ('MB_GetQueueStatus', c_int32, (c_void_p,)),
    ('MB_RegisterService', None, (c_void_p, st_service_p, st_service_p, c_char_p, c_char_p, c_enun_p)),
    ('MB_WaitStart', c_int32, (c_void_p, c_char_p, c_char_p, c_int_p)),
    ('MB_GetTokenName', c_char_p, (c_enun,)),
    ('MB_GetTokenByName', c_enun, (c_char_p,)),
    ('MB_GetTokenByIndex', c_enun, (c_int32,)),
    ('MB_EvtSend', st_msg_p, (c_void_p, st_service_p, c_char_p, c_char_p, c_char_p, c_int, c_int, c_char_p, c_int64, c_enun_p, c_char_p, c_int,)),
    ('MB_EvtSubscribe', c_enun, (c_void_p, st_service_p, c_char_p,)),
    ('MB_EvtUnsubscribe', c_enun, (c_void_p, st_service_p, c_char_p,)),
    # easy message bus API
    ('MB_EasyInitialize', st_easymb_p, (c_char_p, c_enun_p, c_char_p, c_int32)),
    ('MB_EasyRegisterService', None, (st_easymb_p, c_char_p, c_char_p, c_enun_p)),
    ('MB_EasyGetMessage', st_msg_p, (st_easymb_p, c_char_p, c_int32)),
    ('MB_EasySendMessage', st_msg_p, (st_easymb_p, c_char_p, c_int32, c_enun, c_enun, c_void_p, c_int64, c_enun_p, c_char_p, c_int32)),
    ('MB_EasyReplyMessage', c_int32, (st_easymb_p, st_msg_p)),
    ('MB_EasyFinalize', c_enun, (st_easymb_p,)),
    ('MB_EasyWaitStart', c_int32, (c_void_p, c_char_p, c_char_p, c_int_p)),
    ('MB_EasyEvtSend', st_msg_p, (c_void_p, c_char_p, c_char_p, c_char_p, c_int, c_int, c_char_p, c_int64, c_enun_p, c_char_p, c_int,)),
    ('MB_EasyEvtSubscribe', c_enun, (c_void_p, c_char_p,)),
    ('MB_EasyEvtUnsubscribe', c_enun, (c_void_p, c_char_p,)),
)

#
# Private functions
#


def _load_native():
    """ loads native libraries """
    global _load_native, _dll
    _libpath = _find_library("msgbus")
    if not _libpath:
        raise ImportError("Could not find library 'msgbus'.")
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
                "Could not find function '%s' on 'msgbus' library." % name)
        func.restype = restype
        func.argtypes = argtypes
    _init_dll = None


def _caller(up=0):
    """Get file name, line number, function name and
       source text of the caller's caller as 4-tuple:
       (file, line, func, text).
       The optional argument 'up' allows retrieval of
       a caller further back up into the call stack.
       Note, the source text may be None and function
       name may be '?' in the returned result.  In
       Python 2.3+ the file name may be an absolute
       path.
    """
    try:  # just get a few frames
        f = traceback.extract_stack(limit=up + 3)
        if f:
            return f[0]
    except:
        pass
    return ('', 0, '', None)

#
# Public APIs
#


def MB_GetTokenName(token):
    """ MB_GetTokenName(token) -> str
    Retrieves the token name for the given token number
    @param token: {int} - token number
    @return: The token name
    """
    global _dll
    if _init_dll:
        _init_dll()
    return _dll.MB_GetTokenName(token)


def MB_GetTokenByName(tokenName):
    """ MB_GetTokenByName(tokenName) -> int
    Retrieves the token number for the given token name
    @param tokenName: {str} - token name
    @return: The token number
    """
    global _dll
    if _init_dll:
        _init_dll()
    return _dll.MB_GetTokenByName(tokenName)


def MB_GetTokenByIndex(tokenIndex):
    """ MB_GetTokenByName(tokenName) -> int
    Retrieves the token number for the given token name
    @param tokenName: {str} - token name
    @return: The token number
    """
    global _dll
    if _init_dll:
        _init_dll()
    return _dll.MB_GetTokenByIndex(tokenIndex)


class MBService:

    """ MBService(address, port, pservice=None, autodel=True) -> instance

        This class represents a message-bus service.
        Instances of this class wraps the result of a call to MB_CreateService.
        @param address: {str} - Host-name or IP address of the service.
        @param port: {int} - Port of the service.
        @param pservice: {st_service_p} - Optional native service pointer to use.
               If this is passed, given address and port are ignored.
        @param autodel: {bool} - Indicates if the native instance should be released with this python object.
        @return: MBService instance
    """

    def __init__(self, address, port, pservice=None, autodel=True):
        global _dll
        if _init_dll:
            _init_dll()
        call = _caller()
        service_name = 0
        if pservice is not None and isinstance(pservice, basestring):
            service_name = pservice
            pservice = None
        self._pservice = _dll.MB_CreateService(
            address, port, service_name, call[0], call[1]) if (pservice is None) else pservice
        service = self._pservice.contents
        self.addr = service.addr
        self.port = service.port
        self._autodel = autodel

    def __del__(self):
        global _dll
        """Object destructor that release the native instance."""
        if self._autodel and _dll:
            _dll.MB_ReleaseService(self._pservice)


class MBMessage:

    """ class MBMessage
        Wraps a native message-bus message.

        Instances of this class should never be directly created by client applications.
    """
    sign = None  # <: signature
    size = None  # <: data size
    token = None  # <: token
    format = None  # <: format
    destname = None  # <: destination service name (optional)
    data = None  # <: data (may be empty)
    trailer = None  # <: trailer
    crc = None  # <: crc32
    # <: remote host name or IP address - for incoming messages only
    remotehost = None

    def __init__(self, pmsg, autodel=True):
        self._pmsg = pmsg
        self._autodel = autodel
        msg = pmsg.contents
        self.sign = msg.sign
        self.size = msg.size
        self.token = msg.token
        self.format = msg.format
        self.destname = msg.destname
        self.data = string_at(msg.data, self.size) if msg.data else ""
        self.trailer = msg.trailer
        self.crc = msg.crc
        self.remotehost = msg.remotehost

    def __del__(self):
        """
        Object destructor that destroy the native instance.
        """
        global _dll
        if self._autodel and _dll:
            _dll.MB_ReleaseMessage(self._pmsg)


class MBContext:

    """ MBContext(my_service, name) -> MBContext

        This class represents a message-bus context. Most available operations
        are executed thru an instance of this class.
        Instances of this class wraps the result of a call to MB_Initialize.

        Please note that when you create a new context, a new native thread is started to listen to messages.
        @param my_service: {MBService} - Service representing the IP address and port number to listen to messages.
        @param name: {str} - Client identfication (used only for debug and logs).
        @return: Context instance.
        @raise MBException: if the call to MB_Initialize results in a status different than SE_SUCCESS.
    """

    def __init__(self, my_service, name):
        global _dll
        if _init_dll:
            _init_dll()
        call = _caller()
        status = c_int32(0)
        self._pctx = _dll.MB_Initialize(
            my_service._pservice, name, c_int32_p(status), call[0], call[1])
        status = status.value
        self._dll = _dll
        if status != 0:
            raise MBException("Error calling MB_Initialize.", status)

    def __del__(self):
        """Object destructor that release the native instance."""
        self.MB_Finalize()

    def MB_GetMessage(self, filtermin=0, filtermax=0):
        """ ctx.MB_GetMessage(filtermin=0, filtermax=0) -> MBMessage

            Retrieves and remove the next message in the message queue (blocks until a
            message is available).
            @param filtermin: {int} - Optional token filter start.
            @param filtermax: {int} - Optional token filter end.
            @return: Message instance, or None if the context has been finalized.
        """
        global _dll
        call = _caller()
        pmsg = _dll.MB_GetMessage(
            self._pctx, filtermin, filtermax, call[0], call[1])
        return MBMessage(pmsg, autodel=False) if pmsg else None

    def MB_PeekMessage(self, filtermin=0, filtermax=0):
        """ ctx.MB_PeekMessage(filtermin=0, filtermax=0) -> MBMessage

            Retrieves the next message in the message queue (don't remove it).
            @param filtermin: {int} - Optional token filter start.
            @param filtermax: {int} - Optional token filter end.
            @return: Message instance, or None if the context has been finalized.
        """
        global _dll
        call = _caller()
        pmsg = _dll.MB_PeekMessage(
            self._pctx, filtermin, filtermax, call[0], call[1])
        return MBMessage(pmsg) if pmsg else None

    def MB_SendMessage(self, destination, token, format=0, data=None, timeout=-1):
        """ ctx.MB_SendMessage(destination, token, format=0, data=None, timeout=-1) -> MBMessage

            Sends a message.
            @param destination: {MBService} - Destination service.
            @param token: {int} - Message token.
            @param format: {int} - Optional message format.
            @param data: {str} - Optional data to send.
            @param timeout: {int} - Optional timeout in microseconds (1000000 = 1s).
            @return: Message instance representing the message reply.
            @raise MBTimeout: if the *timeout* param is set and the message timed-out
            @raise MBException: if the call to native MB_SendMessage results in a status different than SE_SUCCESS
        """
        global _dll
        call = _caller()
        size = len(data) if (data is not None) else 0
        status = c_int32(0)
        pmsg = _dll.MB_SendMessage(self._pctx, destination._pservice, size,
                                   token, format, data, timeout, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if SE_TIMEOUT == status:
                raise MBTimeout("Timed-out on MB_SendMessage.", SE_TIMEOUT)
            raise MBException("Error calling MB_SendMessage.", status)
        return MBMessage(pmsg)

    def MB_SendOneWayMessage(self, destination, token, format=0, data=None, timeout=-1):
        """ ctx.MB_SendOneWayMessage(destination, token, format=0, data=None, timeout=-1)

            Sends a message returning as soon as the message arrives to destination.
            @param destination: {MBService} - Destination service.
            @param token: {int} - Message token.
            @param format: {int} - Optional message format.
            @param data: {str} - Optional data to send.
            @param timeout: {int} - Optional timeout in microseconds (1000000 = 1s).
            @raise MBTimeout: if the *timeout* param is set and the message timed-out
            @raise MBException: if the call to native MB_SendMessage results in a status different than SE_SUCCESS
        """
        global _dll
        call = _caller()
        size = len(data) if (data is not None) else 0
        status = c_int32(0)
        _dll.MB_SendOneWayMessage(self._pctx, destination._pservice, size,
                                  token, format, data, timeout, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if SE_TIMEOUT == status:
                raise MBTimeout(
                    "Timed-out on MB_SendOneWayMessage.", SE_TIMEOUT)
            raise MBException("Error calling MB_SendOneWayMessage.", status)

    def MB_ReplyMessage(self, message, format=FM_UNDEFINED, data=None):
        """ ctx.MB_ReplyMessage(message, format=FM_UNDEFINED, data=None) -> int

            Reply a received message.
            @param message: {MBMessage} - Message to reply (set the response token on this message)
            @param format: {int} - Optional response format.
            @param data: {str} - Optinal response data.
            @return status code
        """
        global _dll
        message._pmsg.contents.token = message.token  # Copy the current token to native message before replying
        size = len(data) if (data is not None) else 0
        status = _dll.MB_ReplyMessage(
            self._pctx, message._pmsg, size, format, data)
        message._autodel = False  # Native message has been deleted already
        return status

    def MB_LocateService(self, hv_service, service_name, maxretries=5):
        """ ctx.MB_LocateService(hv_service, service_name, maxretries=5) -> MBService

            Contacts the hypervisor to locate a service.
            @param hv_service: {MBService} - Service representing the hypervisor location.
            @param service_name: {str} - Name of the service to locate.
            @param maxretries: {int} - Optional number of retries in case of failure.
            @return: Service instance representing the located service, or None if the service has not been found
            @raise MBException: if the call to native MB_LocateService results in a status different than SE_SUCCESS
        """
        global _dll
        call = _caller()
        status = c_int32(0)
        pser = _dll.MB_LocateService(
            self._pctx, hv_service._pservice, service_name, maxretries, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if status == SE_NOTFOUND:
                return None
            raise MBException("Error calling MB_LocateService.", status)
        return MBService(None, None, pser)

    def MB_GetQueueStatus(self):
        """ ctx.MB_GetQueueStatus() -> int

            Retrieves the current queue status.
            @return: status - 0 if the queue is empty, or > 0 if it has any message. (the returned value is not the quantity)
        """
        global _dll
        return _dll.MB_GetQueueStatus(self._pctx)

    def MB_RegisterService(self, my_service, hv_service, service_type, service_name):
        """ ctx.MB_RegisterService(my_service, hv_service, service_type, service_name)

            Register a service on hypervisor. All registered services can be located by others.
            @param my_service: {MBService} - Service representing where to find the given service name.
            @param hv_service: {MBService} - Service representing the hypervisor location.
            @param service_type: {str} - Service type to register.
            @param service_name: {str} - Service name to register.
            @raise MBException: if the call to native MB_RegisterService results in a status different than SE_SUCCESS
        """
        global _dll
        status = c_int32(0)
        _dll.MB_RegisterService(self._pctx, my_service._pservice,
                                hv_service._pservice, service_type, service_name, c_int32_p(status))
        status = status.value
        if status != 0:
            raise MBException("Error calling MB_RegisterService.", status)

    def MB_WaitStart(self, exported_services=None, required_services=None):
        """ ctx.MB_WaitStart(exported_services=None, required_services=None) -> int

            Waits for the hypervisor to allow us really startup.
            This will handle all the startup conversation with the hipervisor and will return non-zero
            if we must terminate for some reason.
            @param exported_services: {str} - Services to export, in the form: "service1:type1|service2:type2|...etc..."
            @param required_services: {str} - List of services that are required, in the form: "service1|service2|..etc..."
        """
        return _dll.MB_WaitStart(self._pctx, exported_services, required_services, None)

    def MB_EvtSend(self, hv_service, subject, type, xml, synchronous=False, sourceid=0, queue=None, timeout=-1):
        """ ctx.MB_EvtSend(hv_service, subject, type, xml, synchronous=False, sourceid=0, queue=None)

            Send a system event.

            @param hv_service: {str} - {MBService} - Service representing the hypervisor location.
            @param subject: {str} - Event subject
            @param type: {str} - Event type
            @param xml: {str} - Event xml data
            @param synchronous: {bool} - Indicates if this is a synchronous event
            @param sourceid: {int} - Optional POSID number that is sent with the event
            @param queue: {str} - Optional event queue
            @param timeout: {int} - Optional timeout in microseconds (1000000 = 1s).
            @raise MBException: if the call to native MB_EvtSend results in a status different than SE_SUCCESS
            @return {MBMessage} - Response message (only makes sense for synchronous events)
        """
        global _dll
        call = _caller()
        sync = 1 if synchronous else 0
        status = c_int(0)
        pmsg = _dll.MB_EvtSend(self._pctx, hv_service._pservice, subject, type,
                               xml, sync, sourceid, queue, timeout, c_int_p(status), call[0], call[1])
        status = status.value
        if status != SE_SUCCESS:
            raise MBException("Error calling MB_EvtSend.", status)
        return MBMessage(pmsg) if pmsg else None

    def MB_EvtSubscribe(self, hv_service, subject):
        """ ctx.MB_EvtSubscribe(hv_service, subject)

            Subscribe to listen a sytem event.

            @param hv_service: {str} - {MBService} - Service representing the hypervisor location.
            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EvtSubscribe results in a status different than SE_SUCCESS
        """
        global _dll
        status = _dll.MB_EvtSubscribe(
            self._pctx, hv_service._pservice, subject)
        if status != SE_SUCCESS:
            raise MBException("Error calling MB_EvtSubscribe.", status)

    def MB_EvtUnsubscribe(self, hv_service, subject):
        """ ctx.MB_EvtUnsubscribe(hv_service, subject)

            Unsubscribe to listen a sytem event.

            @param hv_service: {str} - {MBService} - Service representing the hypervisor location.
            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EvtUnsubscribe results in a status different than SE_SUCCESS
        """
        global _dll
        status = _dll.MB_EvtUnsubscribe(
            self._pctx, hv_service._pservice, subject)
        if status != SE_SUCCESS:
            raise MBException("Error calling MB_EvtUnsubscribe.", status)

    def MB_Finalize(self):
        """ ctx.MB_Finalize()

        Manually finalize and release this context.
        Please note that this method is automatically executed when this context is garbage-collected.
        """
        if self._pctx:
            self._dll.MB_Finalize(self._pctx)
            self._pctx = None

#
# Easy message bus APIs
#


class MBEasyContext(MBContext):

    """ MBEasyContext(name) -> MBEasyContext

        This class represents an "easy" message-bus context. Most available operations
        are executed thru an instance of this class.
        Instances of this class wraps the result of a call to MB_EasyInitialize.

        Please note that when you create a new context, a new native thread is started to listen to messages.
        @param name: {str} - Client identfication (used only for debug and logs).
        @return: Context instance.
        @raise MBException: if the call to MB_EasyInitialize results in a status different than SE_SUCCESS.
    """
    ser_service = None  # <: {MBService} - service representing the local component IP and port
    # <: {MBService} - service representing the hypervisor's IP and port
    hv_service = None

    def __init__(self, name):
        global _dll
        if _init_dll:
            _init_dll()
        call = _caller()
        status = c_int32(0)
        self._dll = _dll
        self._pectx = _dll.MB_EasyInitialize(
            name, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            raise MBException("Error calling MB_EasyInitialize.", status)
        ectx = self._pectx.contents
        # Storing the "non-easy" context on "_pctx" allows MBContext methods to
        # work too
        self._pctx = ectx.pctx
        self.ser_service = MBService(None, None, ectx.ser, False)
        self.hv_service = MBService(None, None, ectx.hv, False)

    def __del__(self):
        """Object destructor that release the native instance."""
        self.MB_EasyFinalize()

    def MB_EasyRegisterService(self, service_type, service_name):
        """ ectx.MB_EasyRegisterService(service_type, service_name)

            Register a service on hypervisor. All registered services can be located by others.
            @param service_type: {str} - Service type to register.
            @param service_name: {str} - Service name to register.
            @raise MBException: if the call to native MB_EasyRegisterService results in a status different than SE_SUCCESS
        """
        global _dll
        status = c_int32(0)
        _dll.MB_EasyRegisterService(
            self._pectx, service_type, service_name, c_int32_p(status))
        status = status.value
        if status != 0:
            raise MBException("Error calling MB_EasyRegisterService.", status)

    def MB_EasyGetMessage(self):
        """ ectx.MB_EasyGetMessage() -> MBMessage

            Retrieves and remove the next message in the message queue (blocks until a
            message is available).
            @return: Message instance, or None if the context has been finalized.
        """
        global _dll
        call = _caller()
        pmsg = _dll.MB_EasyGetMessage(self._pectx, call[0], call[1])
        return MBMessage(pmsg, autodel=False) if pmsg else None

    def MB_EasySendMessage(self, dest_name, token, format=0, data=None, timeout=-1):
        """ ectx.MB_EasySendMessage(dest_name, token, format=0, data=None, timeout=-1) -> MBMessage

            Sends a message.
            @param dest_name: {str} - Destination service name.
            @param token: {int} - Message token.
            @param format: {int} - Optional message format.
            @param data: {str} - Optional data to send.
            @param timeout: {int} - Optional timeout in microseconds (1000000 = 1s).
            @return: Message instance representing the message reply.
            @raise MBTimeout: if the *timeout* param is set and the message timed-out
            @raise MBException: if the call to native MB_SendMessage results in a status different than SE_SUCCESS
        """
        global _dll
        call = _caller()
        status = c_int32(0)
        size = len(data) if (data is not None) else 0
        pmsg = _dll.MB_EasySendMessage(
            self._pectx, dest_name, size, token, format, data, timeout, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if SE_TIMEOUT == status:
                raise MBTimeout("Timed-out on MB_EasySendMessage.", SE_TIMEOUT)
            raise MBException("Error calling MB_EasySendMessage.", status)
        return MBMessage(pmsg)

    def MB_EasyReplyMessage(self, message):
        """ ectx.MB_EasyReplyMessage(message) -> int

            Reply a received message.
            @param message: {MBMessage} - Message to reply (set the response token on this message)
            @return status code
        """
        global _dll
        message._pmsg.contents.token = message.token  # Copy the current token to native message before replying
        status = _dll.MB_EasyReplyMessage(self._pectx, message._pmsg)
        message._autodel = False  # Native message has been deleted already
        return status

    def MB_EasyWaitStart(self, exported_services=None, required_services=None):
        """ ectx.MB_EasyWaitStart(exported_services=None, required_services=None) -> int

            Waits for the hypervisor to allow us really startup.
            This will handle all the startup conversation with the hipervisor and will return non-zero
            if we must terminate for some reason.
            @param exported_services: {str} - Services to export, in the form: "service1:type1|service2:type2|...etc..."
            @param required_services: {str} - List of services that are required, in the form: "service1|service2|..etc..."
        """
        global _dll
        return _dll.MB_EasyWaitStart(self._pectx, exported_services, required_services, None)

    def MB_EasyEvtSend(self, subject, type, xml, synchronous=False, sourceid=0, queue=None, timeout=-1):
        """ ctx.MB_EasyEvtSend(subject, type, xml, synchronous=False, sourceid=0, queue=None)

            Send a system event.

            @param subject: {str} - Event subject
            @param type: {str} - Event type
            @param xml: {str} - Event xml data
            @param synchronous: {bool} - Indicates if this is a synchronous event
            @param sourceid: {int} - Optional POSID number that is sent with the event
            @param queue: {str} - Optional event queue
            @param timeout: {int} - Optional timeout in microseconds (1000000 = 1s).
            @raise MBException: if the call to native MB_EasyEvtSend results in a status different than SE_SUCCESS
            @return {MBMessage} - Response message (only makes sense for synchronous events)
        """
        global _dll
        call = _caller()
        sync = 1 if synchronous else 0
        status = c_int(0)
        pmsg = _dll.MB_EasyEvtSend(
            self._pectx, subject, type, xml, sync, sourceid, queue, timeout, c_int_p(status), call[0], call[1])
        status = status.value
        if status != SE_SUCCESS:
            raise MBException("Error calling MB_EasyEvtSend.", status)
        return MBMessage(pmsg) if pmsg else None

    def MB_EasyEvtSubscribe(self, subject):
        """ ctx.MB_EasyEvtSubscribe(subject)

            Subscribe to listen a sytem event.

            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EasyEvtSubscribe results in a status different than SE_SUCCESS
        """
        global _dll
        status = _dll.MB_EasyEvtSubscribe(self._pectx, subject)
        if status != SE_SUCCESS:
            raise MBException("Error calling MB_EasyEvtSubscribe.", status)

    def MB_EasyEvtUnsubscribe(self, subject):
        """ ctx.MB_EasyEvtUnsubscribe(subject)

            Unsubscribe to listen a sytem event.

            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EasyEvtUnsubscribe results in a status different than SE_SUCCESS
        """
        global _dll
        status = _dll.MB_EasyEvtUnsubscribe(self._pectx, subject)
        if status != SE_SUCCESS:
            raise MBException("Error calling MB_EasyEvtUnsubscribe.", status)

    def MB_Finalize(self):
        """ ctx.MB_Finalize()
        Alias for MB_EasyFinalize.
        """
        self.MB_EasyFinalize()

    def MB_EasyFinalize(self):
        """ ctx.MB_EasyFinalize()

        Manually finalize and release this context.
        Please note that this method is automatically executed when this context is garbage-collected.
        """
        if self._pectx:
            self._dll.MB_EasyFinalize(self._pectx)
            self._pectx = None
            self._pctx = None

#
# HTTP Message-bus context
# (Send-only)
#


class MBHttpMessage(object):

    """ Fake MBMessage returned by MBHttpContext"""

    def __init__(self, token, format, data):
        self.token = token
        self.data = data


class MBHttpContext(object):

    """ A fake message-bus context that uses the HTTP interface to send messages (receiving messages is not possible)"""

    def __init__(self, host="127.0.0.1", port=8080, prefix="mwapp", httptimeout=-1):
        self.host = str(host)
        self.port = int(port)
        self.prefix = str(prefix)
        self.httptimeout = httptimeout
        self.httptimeout = socket._GLOBAL_DEFAULT_TIMEOUT if self.httptimeout < 0 else self.httptimeout
        self.conn = None

    def MB_EasyWaitStart(self, *args, **kargs):
        return SE_SUCCESS

    def MB_WaitStart(self, *args, **kargs):
        return SE_SUCCESS

    def MB_Finalize(self, *args, **kargs):
        pass

    def MB_EasyFinalize(self, *args, **kargs):
        pass

    def MB_EasySendMessage(self, dest_name, token, format=FM_PARAM, data=None, timeout=-1):
        """ Sends a message using the HTTP interface """
        data = "" if data is None else base64.b64encode(str(data))
        url = "/%s/services/unknown/%s?token=%s&format=%s&timeout=%d&isBase64=true" % (
            self.prefix, dest_name, token, format, timeout)
        if not self.conn:
            self.conn = httplib.HTTPConnection(
                self.host, self.port, timeout=self.httptimeout)
        try:
            self.conn.request("POST", url, data)
        except:
            # Connection error - reconnect and retry
            self.conn = httplib.HTTPConnection(
                self.host, self.port, timeout=self.httptimeout)
            self.conn.request("POST", url, data)
        res = self.conn.getresponse()
        if int(res.status) == 404:
            raise MBException("Service not found", SE_NOTFOUND)
        if int(res.status) != 200:
            if res.getheader("X-error-code") == "TIMEOUT":
                raise MBTimeout("Timed-out on MB_EasySendMessage.", SE_TIMEOUT)
            raise MBException("HTTP error %s" % res.status, SE_UNDEFINED)
        token, format = map(res.getheader, ('X-token', 'X-format'))
        return MBHttpMessage(int(token or 0), int(format or 0), res.read())

#
# Exceptions
#


class MBException(Exception):

    """ Exception raised when any message bus error happen.

        All message bus exceptions contain a field called 'errorcode'
        that can be used to check the native error code that generated
        the exception.
    """

    def __init__(self, message, errorcode):
        message += " Error code: %d(%s)." % (errorcode, sys_errget(errorcode))
        Exception.__init__(self, message)
        self.errorcode = errorcode


class MBTimeout(MBException):

    """Exception raised to signalize a timeout."""
    pass
