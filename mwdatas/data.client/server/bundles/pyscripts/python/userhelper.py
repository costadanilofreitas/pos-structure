import persistence
import datetime
import hmac

from persistence import Driver

_MWPOS_BASE_HMAC = 0x18122008


class UserHelper:
    def __init__(self, mbcontext):
        # type: (msgbus.MBEasyContext) -> None
        self.mbcontext = mbcontext
        self.conn = None  # type: persistence.Connection

    def __enter__(self):
        self.conn = Driver().open(self.mbcontext)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        return exc_val

    def get_all_users(self):
        # type: () -> dict
        return {x.get_entry(0): (x.get_entry(1), x.get_entry(2)) for x in self.conn.select("""select UserId, UserName,
case when FingerPrintMinutiae is NULL then 0 else 1 end as HasPrinterPrint
 from Users""")}

    def get_users_by_level(self, level):
        # type: () -> dict
        return {x.get_entry(0): (x.get_entry(1), x.get_entry(2)) for x in self.conn.select("""select UserId, UserName, case when FingerPrintMinutiae is NULL then 0 else 1 end as HasPrinterPrint from Users where level='%s' """ % (level))}

    def get_user_by_id(self, userid):
        return {x.get_entry(0): x.get_entry(1) for x in self.conn.select("select UserId, UserName from Users where UserId = '%s'" % userid)}

    def add_user(self, userid, username, passwd, admin, fmd_base64):
        # type: (str, etree.XML.ElementTree.Element, str) -> int
        calc = hmac.new(str(int(userid) + _MWPOS_BASE_HMAC))
        calc.update(passwd)
        the_passwd = calc.hexdigest()
        if not fmd_base64:
            return {self.conn.query(
                "insert into Users(UserId, UserName, LongName, Password, Level, Status, AdmissionDate, PayRate) values ('%s','%s','%s','%s',%d,%d,'%s',%f)" % (
                    userid, username, username, the_passwd, 20 if admin else 0, 0, datetime.date.today(), 8.5))}
        else:
            return {self.conn.query(
                "insert into Users(UserId, UserName, LongName, Password, Level, Status, AdmissionDate, PayRate, FingerPrintMinutiae) values ('%s','%s','%s','%s',%d,%d,'%s',%f,x'%s')" % (
                    userid, username, username, the_passwd, 20 if admin else 0, 0, datetime.date.today(), 8.5, fmd_base64.encode("hex")))}

    def change_pass(self, userid, passwd):
        # type: (str, etree.XML.ElementTree.Element, str) -> int
        calc = hmac.new(str(int(userid) + _MWPOS_BASE_HMAC))
        calc.update(passwd)
        the_passwd = calc.hexdigest()
        return {self.conn.query(
            "update Users set Password = '%s' where UserId = '%s'" % (the_passwd, userid))}

    def remove_user(self, userid):
        return {self.conn.query("delete from Users where UserId = %s" % userid)}
        
    def activate_user(self, userid, op):
        # op = 0 Activate - 1 Deactivate
        return {self.conn.query(
            "update Users set Status = '%d' where UserId = '%s'" % (op, userid))}

    def change_level_user(self, userid, level):
        return {self.conn.query("update Users set level = '%s' where UserId = '%s'" % (level, userid))}

    def get_level_user(self, userid):
        return {'level': x.get_entry(0) for x in self.conn.select("select level from Users where UserId = '%s'" % (userid))}

    def get_user_session(self, posid):
        return {x.get_entry(0): x.get_entry(1) for x in self.conn.select("""
          select us.sessionid, u.level from posctrl.UserSession us join Users u on u.userid = us.operatorid where us.closetime IS NULL and us.posid = '%s'""" % (posid))}
