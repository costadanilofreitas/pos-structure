from helper import ExtendedEnum


class MwSysErrors(ExtendedEnum):

    SE_UNKOWNUSR = "5000"         # unknown user id
    SE_INVALIDPASSWD = "5001"     # invalid password
    SE_DAYNOTCLOSED = "5002"      # business day is not closed
    SE_DAYNOTOPENED = "5003"      # business day is not opened
    SE_OPERLOGGEDIN = "5004"      # operator is still logged in
    SE_OPERNOTLOGGEDIN = "5005"   # operator is not logged in
    SE_ORDEROPENED = "5006"       # there are a sale order opened
    SE_OPEROPENED = "5007"        # there are operators opened in the account database
