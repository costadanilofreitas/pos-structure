# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\wrappers\python\msgbus.py
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


SU_FRESH = 1
TK_SYS_ACK = 4027580417L
TK_SYS_NAK = 4027580418L
TK_SYS_CHECKFORUPDATES = 1048579
TK_HV_COMPSTART = 2097153
TK_HV_COMPSTOP = 2097154
TK_HV_COMPKILL = 4028628994L
TK_HV_COMPLIST = 2097155
TK_HV_QUERY_SERVICE = 2097156
TK_HV_FIND_SERVICE = 2097157
TK_HV_QUERY_BY_TYPE = 2097158
TK_HV_START_COMP = 2097159
TK_HV_SERVICEONLINE = 2097160
TK_HV_SERVICEOFFLINE = 2097161
TK_HV_RESTART = 2097162
TK_HV_GLOBALRESTART = 2097163
TK_HV_GETSTATE = 2097164
TK_HV_SETSTATE = 2097165
TK_HV_LOG = 2097166
TK_HV_GETLICENSE = 2097167
TK_HV_LOGLEVEL = 4028629008L
TK_HV_LISTHVS = 2097184
TK_HV_CHECK_LICENSE_SIGNATURE = 2097200
TK_CMP_TERM_NOW = 4029677569L
TK_CMP_GETSERVICES = 4029677570L
TK_CMP_GETDEPENDS = 4029677571L
TK_CMP_REGSERVICE = 4029677572L
TK_CMP_START = 4029677573L
TK_CMP_MESSAGE = 4029677574L
TK_EVT_EVENT = 4030726145L
TK_EVT_SUBSCRIBE = 4030726146L
TK_EVT_UNSUBSCRIBE = 4030726147L
TK_EVT_RUNTESTS = 4030726148L
TK_EVT_GETLISTENERS = 4030726149L
TK_POS_GETMODEL = 4031774721L
TK_POS_SETSCREEN = 4031774722L
TK_POS_EXECUTEACTION = 4031774723L
TK_POS_MODELSETCUSTOM = 4031774724L
TK_POS_SETINFOMSG = 4031774725L
TK_POS_SHOWDIALOG = 4031774726L
TK_POS_DIALOGRESP = 4031774727L
TK_POS_BUSINESSBEGIN = 4031774728L
TK_POS_BUSINESSEND = 4031774729L
TK_POS_USERLOGIN = 4031774730L
TK_POS_USERPAUSE = 4031774731L
TK_POS_USERLOGOUT = 4031774732L
TK_POS_SETDEFSERVICE = 4031774733L
TK_POS_SETLANG = 4031774734L
TK_POS_SETMAINSCREEN = 4031774735L
TK_POS_SETPOD = 4031774736L
TK_POS_SETFUNCTION = 4031774737L
TK_POS_USEROPEN = 4031774738L
TK_POS_SETMODIFIERSDATA = 4031774739L
TK_POS_ASYNCACTION = 4031774740L
TK_POS_GETSTATE = 4031774741L
TK_POS_GETCONFIG = 4031774742L
TK_POS_LISTUSERS = 4031774743L
TK_POS_SETRECALLDATA = 4031774744L
TK_POS_GETPOSLIST = 4031774745L
TK_POS_UPDATEDIALOG = 4031774746L
TK_KDS_GETMODEL = 4038066177L
TK_KDS_UPDATEVIEW = 4038066178L
TK_KDS_REFRESH = 4038066179L
TK_KDS_REFRESH_END = 4038066180L
TK_KDS_SET_PROD_STATE = 4038066181L
TK_KDS_UNDO_SERVE = 4038066182L
TK_KDS_CHANGE_VIEW = 4038066183L
TK_KDS_TOGGLE_TAG_LINE = 4038066184L
TK_KDS_GLOBAL_SERVE = 4038066185L
TK_KDS_REFRESH_VIEW = 4038066192L
TK_KDS_DISABLE_VIEW = 4038066193L
TK_KDS_UPDATE_INFO = 4038066194L
TK_KDS_ENABLE_VIEW = 4038066195L
TK_KDS_RELOAD = 4038066196L
TK_KIOSK_GETMODEL = 4056940545L
TK_KIOSK_SETLANG = 4056940546L
TK_KIOSK_GETSTATE = 4056940547L
TK_KIOSK_SETSTATE = 4056940548L
TK_KIOSK_CHECKFORUPDATES = 4056944641L
TK_KIOSK_EXECUTEACTION = 4056944642L
TK_KIOSK_PROVIDER_RESERVE = 4056948737L
TK_KIOSK_PROVIDER_CONFIRM = 4056948738L
TK_KIOSK_PROVIDER_DISMISS = 4056948739L
TK_KIOSK_TRANSACTION_PICTURE = 4056952833L
TK_FISCAL_CMD = 4032823297L
TK_PRN_PRINT = 4032823553L
TK_PRN_GETSTATUS = 4032823554L
TK_CDRAWER_OPEN = 4032823809L
TK_CDRAWER_GETSTATUS = 4032823810L
TK_LDISP_WRITE = 4032824065L
TK_LDISP_MARQUEE = 4032824066L
TK_MSR_REQUESTSWIPE = 4032824322L
TK_COIN_DISPENSE = 4032825345L
TK_COIN_GETSTATUS = 4032825346L
TK_COIN_SETUP = 4032825347L
TK_COIN_RESET = 4032825348L
TK_COIN_EXAMINE = 4032825349L
TK_COIN_ADJUST = 4032825350L
TK_COIN_COLLECT = 4032825351L
TK_IMGCAP_CAPTURE = 4032825601L
TK_BUZZER_SOUND = 4032826113L
TK_CTRLUNIT_REGISTER_SALE = 4032826113L
TK_CTRLUNIT_REGISTER_RETURN = 4032826114L
TK_CTRLUNIT_WRITE_JOURNAL = 4032826115L
TK_DRV_IOCTL = 4032888831L
TK_I18N_GETTABLE = 7340033
TK_I18N_GETMSG = 7340034
TK_I18N_TRANSLATE = 7340035
TK_I18N_GETLANGS = 7340036
TK_I18N_GETTABLEJSON = 7340037
TK_L10N_TOCURRENCY = 7340038
TK_L10N_TONUMBER = 7340039
TK_L10N_TODATE = 7340040
TK_L10N_TOTIME = 7340041
TK_L10N_TODATETIME = 7340042
TK_L10N_FROMCURRENCY = 7340043
TK_L10N_FROMNUMBER = 7340044
TK_L10N_FROMDATE = 7340045
TK_L10N_FROMTIME = 7340046
TK_L10N_FROMDATETIME = 7340047
TK_PERSIST_QUERYEXEC = 8388609
TK_PERSIST_CONNALLOC = 8388610
TK_PERSIST_CONNRELEASE = 8388611
TK_PERSIST_SCRIPTEXEC = 8388612
TK_PERSIST_PROCEXEC = 8388613
TK_PERSIST_EXPORTDB = 8388614
TK_PERSIST_IMPORTDB = 8388615
TK_PERSIST_LISTDBS = 8388616
TK_PERSIST_GETINSTNBR = 8388617
TK_PURGE_DB = 8388618
TK_PERSIST_INITTHRDTERM = 8388619
TK_PERSIST_INITINPROGRESS = 8388620
TK_PERSIST_SEQUENCER_INCREMENT = 8388621
TK_PERSIST_GET_PROCEDURES_LIST = 8388622
TK_PERSIST_GET_PROCEDURE_PARAMS = 8388623
TK_PERSIST_SEQUENCER_RESET = 8388624
TK_PERSIST_CHECKCONNECTION = 8388625
TK_REPLICATE = 4034920456L
TK_REPLICA_ACQUIRE = 4034920457L
TK_REPLICA_LISTDBS = 4034920464L
TK_REPLICA_GETCHKPNT = 4034920465L
TK_REPLICA_GETFAILOVERCHKPNT = 4034920466L
TK_REPLICA_GETUSERVERSION = 4034920467L
TK_SLCTRL_PMGR_MAINMENU = 9437185
TK_SLCTRL_PMGR_CUSTOMPARAM = 9437186
TK_SLCTRL_PMGR_PRODUCTSBYTAGS = 9437187
TK_SLCTRL_PMGR_PRODUCTDIM = 9437188
TK_SLCTRL_OMGR_DOSALE = 10485761
TK_SLCTRL_OMGR_ORDERPICT = 10485762
TK_SLCTRL_OMGR_VOIDLINE = 10485763
TK_SLCTRL_OMGR_VOIDORDER = 10485764
TK_SLCTRL_OMGR_LISTOPTIONS = 10485765
TK_SLCTRL_OMGR_ORDERTOTAL = 10485766
TK_SLCTRL_OMGR_CLEAROPTION = 10485767
TK_SLCTRL_OMGR_SPLITORDER = 10485768
TK_SLCTRL_OMGR_SPLITORDERLINE = 10485769
TK_SLCTRL_OMGR_DOOPTION = 10485770
TK_SLCTRL_OMGR_STOREORDER = 10485771
TK_SLCTRL_OMGR_RECALLORDER = 10485772
TK_SLCTRL_OMGR_LISTORDERS = 10485773
TK_SLCTRL_OMGR_CHANGEQTY = 10485774
TK_SLCTRL_OMGR_ORDERREOPEN = 10485775
TK_SLCTRL_OMGR_DOTENDER = 10485776
TK_SLCTRL_OMGR_CLEARTENDERS = 10485777
TK_SLCTRL_OMGR_LISTMODIFIERS = 10485778
TK_SLCTRL_OMGR_CHANGEMODIFIER = 10485779
TK_SLCTRL_OMGR_CHANGEDIMENSION = 10485780
TK_SLCTRL_OMGR_RESETCURRORDER = 10485781
TK_SLCTRL_OMGR_SETLSTSALELINE = 10485782
TK_SLCTRL_OMGR_UPDPROPERTIES = 10485783
TK_SLCTRL_OMGR_CREATEORDER = 10485784
TK_SLCTRL_OMGR_CHANGEMODIFIERS = 10485785
TK_SLCTRL_OMGR_VOIDHISTORY = 10485786
TK_SLCTRL_OMGR_PRICEOVERWRITE = 10485787
TK_SLCTRL_OMGR_LISTOPTSOLUTIONS = 10485788
TK_SLCTRL_OMGR_SETCUSTOMPROPERTY = 10485789
TK_SLCTRL_OMGR_GETCUSTOMPROPERTY = 10485790
TK_SLCTRL_OMGR_LIST_DISCOUNTS = 10485791
TK_SLCTRL_OMGR_APPLY_DISCOUNT = 10485792
TK_SLCTRL_OMGR_CLEAR_DISCOUNT = 10485793
TK_SLCTRL_OMGR_MERGE_ORDERS = 10485794
TK_SLCTRL_OMGR_EXTRAMODIFIERS = 10485795
TK_SLCTRL_OMGR_DOMULTIOPTIONS = 10485796
TK_SLCTRL_OMGR_ADDCOMMENT = 10485797
TK_SLCTRL_OMGR_DELCOMMENT = 10485798
TK_SLCTRL_OMGR_UPDCOMMENT = 10485799
TK_SLCTRL_OMGR_SETCUSTOMPROPERTIES = 10485800
TK_SLCTRL_OMGR_FRACTIONATELINE = 10485801
TK_SLCTRL_OMGR_REVERTLINEFRACTION = 10485808
TK_SLCTRL_OMGR_RESETORDERTENDER = 10485809
TK_SLCTRL_RESET = 39845889
TK_PROD_REFRESHVIEW = 12582913
TK_PROD_SETORDERSTATE = 12582914
TK_PROD_CRASHPOINT = 12582915
TK_PROD_CAPTUREIMAGE = 12582916
TK_PROD_RETRIEVEIMAGE = 12582917
TK_PROD_SIDEONOFF = 12582918
TK_PROD_UNDOSERVE = 12582919
TK_PROD_TOGGLETAGLINE = 12582920
TK_PROD_GLOBAL_SERVE = 12582921
TK_PROD_DISABLE_VIEW = 12582928
TK_PROD_ENABLE_VIEW = 12582929
TK_PROD_REDIRECT_BOX = 12582930
TK_PROD_RESTORE_BOX = 12582931
TK_REPORT_GENERATE = 13631489
TK_ACCOUNT_TRANSFER = 14680065
TK_ACCOUNT_GETTRANSFERS = 14680066
TK_ACCOUNT_GETTOTALS = 14680067
TK_ACCOUNT_GIFTCARDACTIVITY = 14680068
TK_ACCOUNT_EFTACTIVITY = 14680069
TK_EFT_REQUEST = 15728641
TK_GENESIS_GETVERSION = 16777217
TK_GENESIS_LISTFILES = 16777218
TK_GENESIS_GETFILE = 16777219
TK_GENESIS_LISTPKGS = 16777220
TK_GENESIS_APPLYUPDATE = 16777221
TK_GENESIS_ROLLBACKUPDATE = 16777222
TK_TIMEPUNCH_OPER = 17825793
TK_TIMEPUNCH_REPORT = 17825794
TK_TIMEPUNCH_GETJOBCODES = 17825795
TK_USERCTRL_AUTHENTICATE = 18874369
TK_USERCTRL_GETINFO = 18874370
TK_USERCTRL_GETINFO_BADGE = 18874371
TK_STORECFG_GET = 19922945
TK_STORECFG_GETFULL = 19922946
TK_STORECFG_SET = 19922947
TK_AUDITLOG_RESYNC = 4047503361L
TK_BOINVENTORY_UNUSED = 22020096
TK_BOINVENTORY_MANAGE_SUPPLIER = 22020097
TK_BOINVENTORY_MANAGE_SUPPLIER_PRODUCTS = 22020098
TK_BOINVENTORY_MANAGE_SUPPLIER_INVOICES = 22020099
TK_BOINVENTORY_MANAGE_STORAGE_AREAS = 22020100
TK_BOINVENTORY_MANAGE_DEPARTMENTS = 22020101
TK_BOINVENTORY_MANAGE_GROUPS = 22020102
TK_BOINVENTORY_MANAGE_ITEMS = 22020103
TK_BOINVENTORY_MANAGE_BOM = 22020104
TK_BOINVENTORY_MANAGE_INVENTORY_COUNTS = 22020105
TK_BOINVENTORY_IMPORT_POS_SALES = 22020106
TK_BOINVENTORY_INVENTORY_CONTROL = 22020107
TK_BOINVENTORY_INVOICES_AVAILABLE = 22020108
TK_BOINVENTORY_SALES_AVAILABLE = 22020109
TK_BOINVENTORY_INVENTORY_TRANSACTION = 22020110
TK_BOINVENTORY_DELIVERY_TRANSACTION = 22020111
TK_BOINVENTORY_POS_SALES_TRANSACTION = 22020112
TK_BOINVENTORY_DELIVERY_TRANSACTION_DETAILS = 22020113
TK_BOINVENTORY_POS_SALES_TRANSACTION_DETAILS = 22020114
TK_BOINVENTORY_COUNT_ADJUSTMENT_TRANSACTION = 22020115
TK_BOINVENTORY_DELIVERY_ADJUSTMENT_TRANSACTION = 22020116
TK_BOINVENTORY_SUBINVENTORY_TRANSFER_TRANSACTION = 22020117
TK_BOINVENTORY_INBOUND_TRANSFER_TRANSACTION = 22020118
TK_BOINVENTORY_OUTBOUND_TRANSFER_TRANSACTION = 22020119
TK_BOINVENTORY_SUPPLIER_RETURN_TRANSACTION = 22020120
TK_BOINVENTORY_WIP_SCRAP_TRANSACTION = 22020121
TK_BOINVENTORY_INVENTORY_RESET = 22020122
TK_BOINVENTORY_REPORTS = 22020123
TK_BOINVENTORY_MANAGE_ASSEMBLY = 22020124
TK_BOINVENTORY_MANAGE_ITEM_PACKAGES = 22020125
TK_BOINVENTORY_MANAGE_PLU_LIST = 22020126
TK_BOCASH_REPORTS = 23068672
TK_BOCASH_MANAGE_STORECFG = 23068673
TK_BOCASH_MANAGE_BUSINESSWEEK = 23068674
TK_BOCASH_MANAGE_DRAWERCOUNT_TEMPLATE = 23068675
TK_BOCASH_MANAGE_BUSINESSDATE = 23068676
TK_BOCASH_POSEVENTS_DAYOPEN = 23068677
TK_BOCASH_POSEVENTS_DAYCLOSE = 23068678
TK_BOCASH_POSEVENTS_SKIM = 23068679
TK_BOCASH_POSEVENTS_DRAWERCHANGE = 23068680
TK_BOCASH_MANAGE_DRAWERCOUNT = 23068681
TK_BOCASH_MANAGE_DRAWERCOUNT_DETAILS = 23068682
TK_BOCASH_MANAGE_TRANSACTIONS = 23068683
TK_BOCASH_MANAGE_TRANSACTION_DETAILS = 23068684
TK_BOCASH_POSEVENTS_HISTORY = 23068685
TK_BOCASH_FORCE_WEEK_CLOSE = 23068686
TK_BOREPORT_REPORTS = 25165824
TK_BOREPORT_MANAGE_TEMPLATE = 25165825
TK_BOREPORT_MANAGE_WORKBOOK = 25165826
TK_BOREPORT_MANAGE_WORKSHEET = 25165827
TK_BOREPORT_MANAGE_WORKSHEET_CELLS = 25165828
TK_BOREPORT_WORKBOOK_FILE = 25165829
TK_BOREPORT_WORKBOOK_SOLVER = 25165830
TK_BOREPORT_WORKBOOK_PREVIEW = 25165831
TK_BOREPORT_GETCONFIG = 25165832
TK_BOACCOUNT_REPORTS = 24117248
TK_BOACCOUNT_MANAGE_TRNTYPE = 24117249
TK_BOACCOUNT_MANAGE_CHARTOFACCOUNTS = 24117250
TK_BOACCOUNT_MANAGE_JOURNALTEMPLATE = 24117251
TK_BOACCOUNT_MANAGE_JOURNAL = 24117252
TK_BOACCOUNT_MANAGE_TRIALBALANCE = 24117253
TK_BOLABOR_REPORTS = 29360128
TK_BOLABOR_MANAGE_EMPLOYEES = 29360129
TK_BOLABOR_MANAGE_TIMEPUNCHES = 29360130
TK_BOLABOR_MANAGE_EMPLOYEE_CUSTOMDATA = 29360131
TK_CASHLESS_REPORT = 26214401
TK_GUI_REQUESTFOCUS = 27262977
TK_GUI_SETURL = 27262978
TK_GUI_EVALJS = 27262979
TK_GUI_MINIMIZE = 27262980
TK_CALLCENTER_GETSTATUS = 28311553
TK_CALLCENTER_AGTLOGIN = 28311554
TK_CALLCENTER_SETAGTSTATE = 28311555
TK_CALLCENTER_NEWCALL = 28311556
TK_CALLCENTER_CALLENDED = 28311557
TK_CALLCENTER_AGTSTATECHANGED = 28311558
TK_CALLCENTER_RECONNECT = 28311559
TK_CALLCENTER_SETVOLUME = 28311560
TK_CALLCENTER_TRANSFER = 28311561
TK_CALLCENTER_HEARTHBEAT = 28311562
TK_CALLCENTER_EXITAPP = 28311563
TK_CALLCENTER_SETFAILOVER = 28311564
TK_CALLCENTER_SHOWALERT = 28311565
TK_CALLCENTER_MANAGEBTREST = 28311566
TK_LS_RETRIEVE_CACHE = 31457281
TK_LS_STORE_CACHE = 31457282
TK_LS_CREATE_SESSION = 31457283
TK_LS_STORE_PURCHASE = 31457284
TK_LS_VOID_PURCHASE = 31457285
TK_BUF_BUFFER_PURCHASE = 32505857
TK_BUF_PAY_ORDER = 32505858
TK_BUF_STORE_API_CALL = 32505859
TK_BUF_FINISH_ORDER = 32505860
TK_ML_REFRESH_CACHE = 33554433
TK_KIOSKCTRL_DBUPDATE = 34603009
TK_KIOSKCTRL_GENESISUPDATE = 34603010
TK_KIOSKCTRL_IMAGESUPDATE = 34603011
TK_CATERING_NEWEVENT = 35651585
TK_CATERING_STORECUSTOMER = 35651586
TK_CATERING_SEARCHCUSTOMER = 35651587
TK_CATERING_UPDATECUSTOMER = 35651588
TK_CATERING_UPDATEEVENT = 35651589
TK_CATERING_UPDATEBILLINGID = 35651590
TK_CATERING_ORDERPICT_TO_JSON = 35651591
TK_CATERING_GETCAFEINFO = 35651592
TK_CATERING_GETEVENT = 35651593
TK_ROPECTRL_SEND_XML = 36700161
TK_ROPECTRL_ROPE_XML = 36700162
TK_BOH_MESSAGE = 37748737
TK_BOH_UPLOADORDER = 37748738
TK_LOYALTY_AUTHENTICATE = 38797313
TK_LOYALTY_BALANCE = 38797314
TK_LOYALTY_APPLY = 38797315
TK_LOYALTY_VOID = 38797316
TK_LOYALTY_REFUND = 38797317
TK_LOYALTY_COMMAND = 38797318
FM_UNDEFINED = 0
FM_XML = 1
FM_PARAM = 2
FM_ADDR_PORT = 3
FM_INT32 = 4
FM_INT64 = 5
FM_STRING = 6
FM_STR_ARRAY_PIPE = 7
FM_IMG_JPG = 8
FM_IMG_PNG = 9
FM_IMG_GIF = 10
FM_PDF = 11
FM_SWAGGER = 12

class st_msg(Structure):
    _fields_ = [('sign', c_int32),
     ('size', c_int32),
     ('token', c_uint32),
     ('format', c_int32),
     ('destname', c_char_p),
     ('data', c_void_p),
     ('trailer', c_int32),
     ('crc', c_int32),
     ('remotehost', c_char_p)]


st_msg_p = POINTER(st_msg)

class st_service(Structure):
    _fields_ = [('addr', c_char_p), ('port', c_int32), ('name', c_char_p)]


st_service_p = POINTER(st_service)

class st_easymb(Structure):
    _fields_ = [('pctx', c_void_p),
     ('ser', st_service_p),
     ('hv', st_service_p),
     ('opaque', c_void_p)]


st_easymb_p = POINTER(st_easymb)
c_enun = c_int
c_enun_p = POINTER(c_enun)
c_int_p = POINTER(c_int)
c_int32_p = POINTER(c_int32)
c_char_pp = POINTER(c_char_p)
_funcdefs = (('MB_CreateService', st_service_p, (c_char_p,
   c_int32,
   c_void_p,
   c_char_p,
   c_int32)),
 ('MB_Initialize', c_void_p, (st_service_p,
   c_char_p,
   c_enun_p,
   c_char_p,
   c_int32)),
 ('MB_GetMessage', st_msg_p, (c_void_p,
   c_enun,
   c_enun,
   c_char_p,
   c_int32)),
 ('MB_SendMessage', st_msg_p, (c_void_p,
   st_service_p,
   c_int32,
   c_enun,
   c_enun,
   c_char_p,
   c_int64,
   c_enun_p,
   c_char_p,
   c_int32)),
 ('MB_SendOneWayMessage', None, (c_void_p,
   st_service_p,
   c_int32,
   c_enun,
   c_enun,
   c_char_p,
   c_int64,
   c_enun_p,
   c_char_p,
   c_int32)),
 ('MB_PeekMessage', st_msg_p, (c_void_p,
   c_enun,
   c_enun,
   c_char_p,
   c_int32)),
 ('MB_ReplyMessage', c_int32, (c_void_p,
   st_msg_p,
   c_int32,
   c_enun,
   c_char_p)),
 ('MB_LocateService', st_service_p, (c_void_p,
   st_service_p,
   c_char_p,
   c_int32,
   c_enun_p,
   c_char_p,
   c_int32)),
 ('MB_ReleaseService', c_enun, (st_service_p,)),
 ('MB_Finalize', c_enun, (c_void_p,)),
 ('MB_FinalizeAll', c_enun, ()),
 ('MB_ReleaseMessage', None, (st_msg_p,)),
 ('MB_GetQueueStatus', c_int32, (c_void_p,)),
 ('MB_RegisterService', None, (c_void_p,
   st_service_p,
   st_service_p,
   c_char_p,
   c_char_p,
   c_enun_p)),
 ('MB_WaitStart', c_int32, (c_void_p,
   c_char_p,
   c_char_p,
   c_int_p)),
 ('MB_GetTokenName', c_char_p, (c_enun,)),
 ('MB_GetTokenByName', c_enun, (c_char_p,)),
 ('MB_GetTokenByIndex', c_enun, (c_int32,)),
 ('MB_EvtSend', st_msg_p, (c_void_p,
   st_service_p,
   c_char_p,
   c_char_p,
   c_char_p,
   c_int,
   c_int,
   c_char_p,
   c_int64,
   c_enun_p,
   c_char_p,
   c_int)),
 ('MB_EvtSubscribe', c_enun, (c_void_p, st_service_p, c_char_p)),
 ('MB_EvtUnsubscribe', c_enun, (c_void_p, st_service_p, c_char_p)),
 ('MB_EasyInitialize', st_easymb_p, (c_char_p,
   c_enun_p,
   c_char_p,
   c_int32)),
 ('MB_EasyRegisterService', None, (st_easymb_p,
   c_char_p,
   c_char_p,
   c_enun_p)),
 ('MB_EasyGetMessage', st_msg_p, (st_easymb_p, c_char_p, c_int32)),
 ('MB_EasySendMessage', st_msg_p, (st_easymb_p,
   c_char_p,
   c_int32,
   c_enun,
   c_enun,
   c_void_p,
   c_int64,
   c_enun_p,
   c_char_p,
   c_int32)),
 ('MB_EasyReplyMessage', c_int32, (st_easymb_p, st_msg_p)),
 ('MB_EasyFinalize', c_enun, (st_easymb_p,)),
 ('MB_EasyWaitStart', c_int32, (c_void_p,
   c_char_p,
   c_char_p,
   c_int_p)),
 ('MB_EasyEvtSend', st_msg_p, (c_void_p,
   c_char_p,
   c_char_p,
   c_char_p,
   c_int,
   c_int,
   c_char_p,
   c_int64,
   c_enun_p,
   c_char_p,
   c_int)),
 ('MB_EasyEvtSubscribe', c_enun, (c_void_p, c_char_p)),
 ('MB_EasyEvtUnsubscribe', c_enun, (c_void_p, c_char_p)))

def _load_native():
    """ loads native libraries """
    global _load_native
    global _dll
    _libpath = _find_library('msgbus')
    if not _libpath:
        raise ImportError("Could not find library 'msgbus'.")
    _dll = cdll.LoadLibrary(_libpath)
    _load_native = None
    return


def _init_dll():
    """
    Perform the DLL initialization inside a function, to avoid
    leaving variables in the module scope
    """
    global _init_dll
    if _load_native:
        _load_native()
    for name, restype, argtypes in _funcdefs:
        func = getattr(_dll, name, None)
        if func is None:
            raise ImportError("Could not find function '%s' on 'msgbus' library." % name)
        func.restype = restype
        func.argtypes = argtypes

    _init_dll = None
    return


def _caller(up = 0):
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
    try:
        f = traceback.extract_stack(limit=up + 3)
        if f:
            return f[0]
    except:
        pass

    return ('', 0, '', None)


def MB_GetTokenName(token):
    """ MB_GetTokenName(token) -> str
    Retrieves the token name for the given token number
    @param token: {int} - token number
    @return: The token name
    """
    if _init_dll:
        _init_dll()
    return _dll.MB_GetTokenName(token)


def MB_GetTokenByName(tokenName):
    """ MB_GetTokenByName(tokenName) -> int
    Retrieves the token number for the given token name
    @param tokenName: {str} - token name
    @return: The token number
    """
    if _init_dll:
        _init_dll()
    return _dll.MB_GetTokenByName(tokenName)


def MB_GetTokenByIndex(tokenIndex):
    """ MB_GetTokenByName(tokenName) -> int
    Retrieves the token number for the given token name
    @param tokenName: {str} - token name
    @return: The token number
    """
    if _init_dll:
        _init_dll()
    return _dll.MB_GetTokenByIndex(tokenIndex)


class MBService():
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

    def __init__(self, address, port, pservice = None, autodel = True):
        if _init_dll:
            _init_dll()
        call = _caller()
        service_name = 0
        if pservice is not None and isinstance(pservice, basestring):
            service_name = pservice
            pservice = None
        self._pservice = _dll.MB_CreateService(address, port, service_name, call[0], call[1]) if pservice is None else pservice
        service = self._pservice.contents
        self.addr = service.addr
        self.port = service.port
        self._autodel = autodel
        return

    def __del__(self):
        if self._autodel and _dll:
            _dll.MB_ReleaseService(self._pservice)


class MBMessage():
    """ class MBMessage
        Wraps a native message-bus message.
    
        Instances of this class should never be directly created by client applications.
    """
    sign = None
    size = None
    token = None
    format = None
    destname = None
    data = None
    trailer = None
    crc = None
    remotehost = None

    def __init__(self, pmsg, autodel = True):
        self._pmsg = pmsg
        self._autodel = autodel
        msg = pmsg.contents
        self.sign = msg.sign
        self.size = msg.size
        self.token = msg.token
        self.format = msg.format
        self.destname = msg.destname
        self.data = string_at(msg.data, self.size) if msg.data else ''
        self.trailer = msg.trailer
        self.crc = msg.crc
        self.remotehost = msg.remotehost

    def __del__(self):
        """
        Object destructor that destroy the native instance.
        """
        if self._autodel and _dll:
            _dll.MB_ReleaseMessage(self._pmsg)


class MBContext():
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
        if _init_dll:
            _init_dll()
        call = _caller()
        status = c_int32(0)
        self._pctx = _dll.MB_Initialize(my_service._pservice, name, c_int32_p(status), call[0], call[1])
        status = status.value
        self._dll = _dll
        if status != 0:
            raise MBException('Error calling MB_Initialize.', status)

    def __del__(self):
        """Object destructor that release the native instance."""
        self.MB_Finalize()

    def MB_GetMessage(self, filtermin = 0, filtermax = 0):
        """ ctx.MB_GetMessage(filtermin=0, filtermax=0) -> MBMessage
        
            Retrieves and remove the next message in the message queue (blocks until a
            message is available).
            @param filtermin: {int} - Optional token filter start.
            @param filtermax: {int} - Optional token filter end.
            @return: Message instance, or None if the context has been finalized.
        """
        call = _caller()
        pmsg = _dll.MB_GetMessage(self._pctx, filtermin, filtermax, call[0], call[1])
        if pmsg:
            return MBMessage(pmsg, autodel=False)
        else:
            return None

    def MB_PeekMessage(self, filtermin = 0, filtermax = 0):
        """ ctx.MB_PeekMessage(filtermin=0, filtermax=0) -> MBMessage
        
            Retrieves the next message in the message queue (don't remove it).
            @param filtermin: {int} - Optional token filter start.
            @param filtermax: {int} - Optional token filter end.
            @return: Message instance, or None if the context has been finalized.
        """
        call = _caller()
        pmsg = _dll.MB_PeekMessage(self._pctx, filtermin, filtermax, call[0], call[1])
        if pmsg:
            return MBMessage(pmsg)
        else:
            return None

    def MB_SendMessage(self, destination, token, format = 0, data = None, timeout = -1):
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
        call = _caller()
        size = len(data) if data is not None else 0
        status = c_int32(0)
        pmsg = _dll.MB_SendMessage(self._pctx, destination._pservice, size, token, format, data, timeout, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if SE_TIMEOUT == status:
                raise MBTimeout('Timed-out on MB_SendMessage.', SE_TIMEOUT)
            raise MBException('Error calling MB_SendMessage.', status)
        return MBMessage(pmsg)

    def MB_SendOneWayMessage(self, destination, token, format = 0, data = None, timeout = -1):
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
        call = _caller()
        size = len(data) if data is not None else 0
        status = c_int32(0)
        _dll.MB_SendOneWayMessage(self._pctx, destination._pservice, size, token, format, data, timeout, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if SE_TIMEOUT == status:
                raise MBTimeout('Timed-out on MB_SendOneWayMessage.', SE_TIMEOUT)
            raise MBException('Error calling MB_SendOneWayMessage.', status)
        return

    def MB_ReplyMessage(self, message, format = FM_UNDEFINED, data = None):
        """ ctx.MB_ReplyMessage(message, format=FM_UNDEFINED, data=None) -> int
        
            Reply a received message.
            @param message: {MBMessage} - Message to reply (set the response token on this message)
            @param format: {int} - Optional response format.
            @param data: {str} - Optinal response data.
            @return status code
        """
        message._pmsg.contents.token = message.token
        size = len(data) if data is not None else 0
        status = _dll.MB_ReplyMessage(self._pctx, message._pmsg, size, format, data)
        message._autodel = False
        return status

    def MB_LocateService(self, hv_service, service_name, maxretries = 5):
        """ ctx.MB_LocateService(hv_service, service_name, maxretries=5) -> MBService
        
            Contacts the hypervisor to locate a service.
            @param hv_service: {MBService} - Service representing the hypervisor location.
            @param service_name: {str} - Name of the service to locate.
            @param maxretries: {int} - Optional number of retries in case of failure.
            @return: Service instance representing the located service, or None if the service has not been found
            @raise MBException: if the call to native MB_LocateService results in a status different than SE_SUCCESS
        """
        call = _caller()
        status = c_int32(0)
        pser = _dll.MB_LocateService(self._pctx, hv_service._pservice, service_name, maxretries, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if status == SE_NOTFOUND:
                return None
            raise MBException('Error calling MB_LocateService.', status)
        return MBService(None, None, pser)

    def MB_GetQueueStatus(self):
        """ ctx.MB_GetQueueStatus() -> int
        
            Retrieves the current queue status.
            @return: status - 0 if the queue is empty, or > 0 if it has any message. (the returned value is not the quantity)
        """
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
        status = c_int32(0)
        _dll.MB_RegisterService(self._pctx, my_service._pservice, hv_service._pservice, service_type, service_name, c_int32_p(status))
        status = status.value
        if status != 0:
            raise MBException('Error calling MB_RegisterService.', status)

    def MB_WaitStart(self, exported_services = None, required_services = None):
        """ ctx.MB_WaitStart(exported_services=None, required_services=None) -> int
        
            Waits for the hypervisor to allow us really startup.
            This will handle all the startup conversation with the hipervisor and will return non-zero
            if we must terminate for some reason.
            @param exported_services: {str} - Services to export, in the form: "service1:type1|service2:type2|...etc..."
            @param required_services: {str} - List of services that are required, in the form: "service1|service2|..etc..."
        """
        return _dll.MB_WaitStart(self._pctx, exported_services, required_services, None)

    def MB_EvtSend(self, hv_service, subject, type, xml, synchronous = False, sourceid = 0, queue = None, timeout = -1):
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
        call = _caller()
        sync = 1 if synchronous else 0
        status = c_int(0)
        pmsg = _dll.MB_EvtSend(self._pctx, hv_service._pservice, subject, type, xml, sync, sourceid, queue, timeout, c_int_p(status), call[0], call[1])
        status = status.value
        if status != SE_SUCCESS:
            raise MBException('Error calling MB_EvtSend.', status)
        if pmsg:
            return MBMessage(pmsg)
        else:
            return None

    def MB_EvtSubscribe(self, hv_service, subject):
        """ ctx.MB_EvtSubscribe(hv_service, subject)
        
            Subscribe to listen a sytem event.
        
            @param hv_service: {str} - {MBService} - Service representing the hypervisor location.
            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EvtSubscribe results in a status different than SE_SUCCESS
        """
        status = _dll.MB_EvtSubscribe(self._pctx, hv_service._pservice, subject)
        if status != SE_SUCCESS:
            raise MBException('Error calling MB_EvtSubscribe.', status)

    def MB_EvtUnsubscribe(self, hv_service, subject):
        """ ctx.MB_EvtUnsubscribe(hv_service, subject)
        
            Unsubscribe to listen a sytem event.
        
            @param hv_service: {str} - {MBService} - Service representing the hypervisor location.
            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EvtUnsubscribe results in a status different than SE_SUCCESS
        """
        status = _dll.MB_EvtUnsubscribe(self._pctx, hv_service._pservice, subject)
        if status != SE_SUCCESS:
            raise MBException('Error calling MB_EvtUnsubscribe.', status)

    def MB_Finalize(self):
        """ ctx.MB_Finalize()
        
        Manually finalize and release this context.
        Please note that this method is automatically executed when this context is garbage-collected.
        """
        if self._pctx:
            self._dll.MB_Finalize(self._pctx)
            self._pctx = None
        return


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
    ser_service = None
    hv_service = None

    def __init__(self, name):
        if _init_dll:
            _init_dll()
        call = _caller()
        status = c_int32(0)
        self._dll = _dll
        self._pectx = _dll.MB_EasyInitialize(name, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            raise MBException('Error calling MB_EasyInitialize.', status)
        ectx = self._pectx.contents
        self._pctx = ectx.pctx
        self.ser_service = MBService(None, None, ectx.ser, False)
        self.hv_service = MBService(None, None, ectx.hv, False)
        return

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
        status = c_int32(0)
        _dll.MB_EasyRegisterService(self._pectx, service_type, service_name, c_int32_p(status))
        status = status.value
        if status != 0:
            raise MBException('Error calling MB_EasyRegisterService.', status)

    def MB_EasyGetMessage(self):
        """ ectx.MB_EasyGetMessage() -> MBMessage
        
            Retrieves and remove the next message in the message queue (blocks until a
            message is available).
            @return: Message instance, or None if the context has been finalized.
        """
        call = _caller()
        pmsg = _dll.MB_EasyGetMessage(self._pectx, call[0], call[1])
        if pmsg:
            return MBMessage(pmsg, autodel=False)
        else:
            return None

    def MB_EasySendMessage(self, dest_name, token, format = 0, data = None, timeout = -1):
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
        call = _caller()
        status = c_int32(0)
        size = len(data) if data is not None else 0
        pmsg = _dll.MB_EasySendMessage(self._pectx, dest_name, size, token, format, data, timeout, c_int32_p(status), call[0], call[1])
        status = status.value
        if status != 0:
            if SE_TIMEOUT == status:
                raise MBTimeout('Timed-out on MB_EasySendMessage.', SE_TIMEOUT)
            raise MBException('Error calling MB_EasySendMessage.', status)
        return MBMessage(pmsg)

    def MB_EasyReplyMessage(self, message):
        """ ectx.MB_EasyReplyMessage(message) -> int
        
            Reply a received message.
            @param message: {MBMessage} - Message to reply (set the response token on this message)
            @return status code
        """
        message._pmsg.contents.token = message.token
        status = _dll.MB_EasyReplyMessage(self._pectx, message._pmsg)
        message._autodel = False
        return status

    def MB_EasyWaitStart(self, exported_services = None, required_services = None):
        """ ectx.MB_EasyWaitStart(exported_services=None, required_services=None) -> int
        
            Waits for the hypervisor to allow us really startup.
            This will handle all the startup conversation with the hipervisor and will return non-zero
            if we must terminate for some reason.
            @param exported_services: {str} - Services to export, in the form: "service1:type1|service2:type2|...etc..."
            @param required_services: {str} - List of services that are required, in the form: "service1|service2|..etc..."
        """
        return _dll.MB_EasyWaitStart(self._pectx, exported_services, required_services, None)

    def MB_EasyEvtSend(self, subject, type, xml, synchronous = False, sourceid = 0, queue = None, timeout = -1):
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
        call = _caller()
        sync = 1 if synchronous else 0
        status = c_int(0)
        pmsg = _dll.MB_EasyEvtSend(self._pectx, subject, type, xml, sync, sourceid, queue, timeout, c_int_p(status), call[0], call[1])
        status = status.value
        if status != SE_SUCCESS:
            raise MBException('Error calling MB_EasyEvtSend.', status)
        if pmsg:
            return MBMessage(pmsg)
        else:
            return None

    def MB_EasyEvtSubscribe(self, subject):
        """ ctx.MB_EasyEvtSubscribe(subject)
        
            Subscribe to listen a sytem event.
        
            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EasyEvtSubscribe results in a status different than SE_SUCCESS
        """
        status = _dll.MB_EasyEvtSubscribe(self._pectx, subject)
        if status != SE_SUCCESS:
            raise MBException('Error calling MB_EasyEvtSubscribe.', status)

    def MB_EasyEvtUnsubscribe(self, subject):
        """ ctx.MB_EasyEvtUnsubscribe(subject)
        
            Unsubscribe to listen a sytem event.
        
            @param subject: {str} - Event subject or subjects separated by spaces
            @raise MBException: if the call to native MB_EasyEvtUnsubscribe results in a status different than SE_SUCCESS
        """
        status = _dll.MB_EasyEvtUnsubscribe(self._pectx, subject)
        if status != SE_SUCCESS:
            raise MBException('Error calling MB_EasyEvtUnsubscribe.', status)

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
        return


class MBHttpMessage(object):
    """ Fake MBMessage returned by MBHttpContext"""

    def __init__(self, token, format, data):
        self.token = token
        self.data = data


class MBHttpContext(object):
    """ A fake message-bus context that uses the HTTP interface to send messages (receiving messages is not possible)"""

    def __init__(self, host = '127.0.0.1', port = 8080, prefix = 'mwapp', httptimeout = -1):
        self.host = str(host)
        self.port = int(port)
        self.prefix = str(prefix)
        self.httptimeout = httptimeout
        self.httptimeout = socket._GLOBAL_DEFAULT_TIMEOUT if self.httptimeout < 0 else self.httptimeout
        self.conn = None
        return

    def MB_EasyWaitStart(self, *args, **kargs):
        return SE_SUCCESS

    def MB_WaitStart(self, *args, **kargs):
        return SE_SUCCESS

    def MB_Finalize(self, *args, **kargs):
        pass

    def MB_EasyFinalize(self, *args, **kargs):
        pass

    def MB_EasySendMessage(self, dest_name, token, format = FM_PARAM, data = None, timeout = -1):
        """ Sends a message using the HTTP interface """
        data = '' if data is None else base64.b64encode(str(data))
        url = '/%s/services/unknown/%s?token=%s&format=%s&timeout=%d&isBase64=true' % (self.prefix,
         dest_name,
         token,
         format,
         timeout)
        if not self.conn:
            self.conn = httplib.HTTPConnection(self.host, self.port, timeout=self.httptimeout)
        try:
            self.conn.request('POST', url, data)
        except:
            self.conn = httplib.HTTPConnection(self.host, self.port, timeout=self.httptimeout)
            self.conn.request('POST', url, data)

        res = self.conn.getresponse()
        if int(res.status) == 404:
            raise MBException('Service not found', SE_NOTFOUND)
        if int(res.status) != 200:
            if res.getheader('X-error-code') == 'TIMEOUT':
                raise MBTimeout('Timed-out on MB_EasySendMessage.', SE_TIMEOUT)
            raise MBException('HTTP error %s' % res.status, SE_UNDEFINED)
        token, format = map(res.getheader, ('X-token', 'X-format'))
        return MBHttpMessage(int(token or 0), int(format or 0), res.read())


class MBException(Exception):
    """ Exception raised when any message bus error happen.
    
        All message bus exceptions contain a field called 'errorcode'
        that can be used to check the native error code that generated
        the exception.
    """

    def __init__(self, message, errorcode):
        message += ' Error code: %d(%s).' % (errorcode, sys_errget(errorcode))
        Exception.__init__(self, message)
        self.errorcode = errorcode


class MBTimeout(MBException):
    """Exception raised to signalize a timeout."""
    pass