# -*- coding: utf-8 -*-
#
# Python wrapper for the "syserrors" header file
#

_lastcode = -1


def _enum(code=0):
    global _lastcode
    _lastcode = code or (_lastcode + 1)
    return _lastcode


# system


SE_SUCCESS = _enum()               # success
SE_UNDEFINED = _enum()             # undefined error
SE_NOTFOUND = _enum()              # requested operation not found
SE_MEMORY = _enum()                # error allocating memory
SE_TIMEOUT = _enum()               # operation timed out
SE_BADPTR = _enum()                # invalid parameter pointer
SE_NOTIMPLEMENTED = _enum()        # command or operation not implemented
SE_BADPARAM = _enum()              # invalid parameters
SE_SUBSCRIBE = _enum()             # error subscribing to event
SE_BADXML = _enum()                # bad xml file
SE_BADRESPONSE = _enum()           # bad response from source
SE_BADSTATE = _enum()              # state not valid for given operation
SE_USERCANCEL = _enum()            # operation cancelled by the user
SE_ALREADY = _enum()               # tried operation is already implemented
SE_NOTSUPPORTED = _enum()          # operation not supported
SE_DONTMATCH = _enum()             # required matching operation wasn't successfull
SE_EXPIRED = _enum()               # date or time expired
SE_LOADLIBRARY = _enum()           # error loading library
SE_GETPROCADDRESS = _enum()        # error getting procedure address
SE_BADVERSION = _enum()            # invalid file version
SE_CONNECT = _enum()               # error connecting to other part
SE_SEND = _enum()                  # error sending command to hardware or connection
SE_RECV = _enum()                  # error receiving command from hardware or connection
SE_NODATA = _enum()                # no data available

# hypervisor specific

SE_DEPENDENCY = _enum(1000)        # dependency missing for some process
SE_CYCLIC = _enum()                # cyclic reference check error
SE_STOP = _enum()                  # error stopping service
SE_LISTSERVICES = _enum()          # error listing hypervisor current services
SE_STARTCMP = _enum()              # error starting component
SE_KILLCMP = _enum()               # error killing component
SE_HOSTNAME = _enum()              # invalid host name

# msgbus

SE_MB_ERR = _enum(2000)            # error initializing msgbus
SE_MB_WAITBUS = _enum()            # error initiating for start msg
SE_MB_BADFORMAT = _enum()          # bad message format
SE_MB_SNDMSG = _enum()             # error in msgbus sendmsg
SE_MB_SERVICE = _enum()            # error creating msgbus service
SE_MB_CONNECT = _enum()            # connection error
SE_MB_NOTINIT = _enum()            # message bus not initialized
SE_MB_ALREADYINIT = _enum()        # message bus already initialized
SE_MB_DUPLICATED = _enum()         # duplicated
SE_MB_BADREQUEST = _enum()         # bad request
SE_MB_BADPORT = _enum()            # invalid port number
SE_MB_BADIP = _enum()              # invalid IP address
SE_MB_SENDHEADER = _enum()         # error sending header
SE_MB_SENDBODY = _enum()           # error sending msg body
SE_MB_SENDTRAILER = _enum()        # error sending trailler
SE_MB_RECEIVE = _enum()            # error receiving msg
SE_MB_RCVHDR = _enum()             # error receiving msg header
SE_MB_RCVBODY = _enum()            # error receiving msg body
SE_MB_RCVTRAILER = _enum()         # error receiving msg trailler

# database access

SE_DBINIT = _enum(3000)            # error initializing database
SE_DBGETDRIVER = _enum()           # error getting database driver
SE_DBOPEN = _enum()                # error opening database
SE_DBCREATE = _enum()              # error creating table
SE_DBDROP = _enum()                # error dropping (deleting) a table
SE_DBSELECT = _enum()              # error performing a database select operation
SE_DBGETROW = _enum()              # error getting row from database
SE_DBGETCOL = _enum()              # error getting col from database
SE_DBISDOWN = _enum()              # database is down=_enum() we will need to reload it
SE_DBTRNOPEN = _enum()             # error during database transaction open
SE_DBTRNCLOSE = _enum()            # error during database transaction close

# fiscal printer specific

SE_FPERROR = _enum(4000)           # fiscal printer error condition
SE_BADDATE = _enum()               # system and printer date doesn't match
SE_VOIDNOTALLOWED = _enum()        # fiscal printer does not allow fiscal coupon void
SE_BLOCKEDBYTIME = _enum()         # fiscal printer is blocked by time
SE_REPORTZDONE = _enum()           # fiscal report Z (end of day) already done for the current business day
SE_OUTOFSYNC = _enum()             # fiscal printer and POS are out of sync
SE_VOIDPOSORDER = _enum()          # error voiding POS order

# posctrl specific

SE_UNKOWNUSR = _enum(5000)         # unknown user id
SE_INVALIDPASSWD = _enum()         # invalid password
SE_DAYNOTCLOSED = _enum()          # business day is not closed
SE_DAYNOTOPENED = _enum()          # business day is not opened
SE_OPERLOGGEDIN = _enum()          # operator is still logged in
SE_OPERNOTLOGGEDIN = _enum()       # operator is not logged in
SE_ORDEROPENED = _enum()           # there are a sale order opened
SE_OPEROPENED = _enum()            # there are operators opened in the account database

# configuration file (loader.cfg)

SE_CFGLOAD = _enum(6000)           # error loading configuration file
SE_CFGREAD = _enum()               # error reading configuration file
SE_CFGKEY = _enum()                # configuration key not found
SE_CFGGROUP = _enum()              # configuration group not found
SE_CFGBADNAME = _enum()            # bad parameter name
SE_CFGCONFLICT = _enum()           # given parameter already exist

# apr specific error codes

SE_APR_MEMPOOL = _enum(100000)     # error creating apr memory pool
SE_APR_PARSECREATE = _enum()       # error creating xml parser
SE_APR_PARSERFEED = _enum()        # error feeding xml into parser
SE_APR_PARSEERROR = _enum()        # error parsing xml file
SE_APR_ENVGET = _enum()            # error retrieving environment variable
SE_APR_LOCKCREATE = _enum()        # error creating lock instance
SE_APR_CREATECONDVAR = _enum()     # error creating conditional variable
SE_APR_WAITCONDVAR = _enum()       # error waiting cond var
SE_APR_DIGEST = _enum()            # error calculating digest
SE_APR_CREATEMUTEX = _enum()       # error creating apr mutex
SE_APR_CREATEATTR = _enum()        # error creating apr thread attr
SE_APR_CREATETHREAD = _enum()      # error creating apr thread
SE_APR_DIR = _enum()               # error in apr dir open
SE_APR_SOCKCREATE = _enum()        # error creating socket
SE_APR_SOCKINFO = _enum()          # error in apr getting socket info
SE_APR_PROCCREATE = _enum()        # error in apr creating process
SE_APR_THREADPOOL = _enum()        # error creating apr thread-pool
SE_APR_SOCKOPTION = _enum()        # error setting socket option
SE_APR_ADDRINFO = _enum()          # error getting addre info
SE_APR_CONNECT = _enum()           # error connecting to server
SE_APR_SENDBUFFER = _enum()        # error sending buffer
SE_APR_RECVBUFFER = _enum()        # error receiving buffer
SE_APR_SOCKOPT = _enum()           # error setting socket option
SE_APR_MEMORY = _enum()            # error allocating memory from memory pool
SE_APR_BIND = _enum()              # error binding socket
SE_APR_MCASTGRP = _enum()          # error joining to multicast group
SE_APR_FILEOPEN = _enum()          # error opening file
