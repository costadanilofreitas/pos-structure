from datetime import datetime, timedelta


class UserUpdateData(object):
    def __init__(self,
                 user_id=None,
                 long_name=None,
                 password=None,
                 level=None,
                 start_date=None,
                 end_date=None,
                 pay_rate=None,
                 status=None):
        # type: (int, str, str, int, str, str, float, int) -> None
        
        self.user_id = user_id
        self.long_name = long_name
        self.password = password
        self.level = level
        self.start_date = start_date
        self.end_date = end_date
        self.pay_rate = pay_rate
        self.status = status

    def fill_user_status(self):
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        now = datetime.now()
        if self.end_date is not None:
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
        else:
            one_day = timedelta(days=1)
            end = now + one_day
            
        active = False
        if start <= now <= end or self.level >= 30:
            active = True
    
        self.status = "0" if active else "1"
