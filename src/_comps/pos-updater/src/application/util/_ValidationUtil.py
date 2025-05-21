from datetime import datetime, time


class ValidationUtil(object):
    @staticmethod
    def is_inside_allowed_window(start_time, end_time):
        # type: (time, time) -> bool
        
        if start_time == end_time:
            return False
    
        now = datetime.now().time()
        is_inside_update_window = start_time <= now <= end_time
        return is_inside_update_window
